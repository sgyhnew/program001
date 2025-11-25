# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from FG.main import Game,SkillData
from dataclasses import dataclass

import random
from time import sleep

from FG.constants import *
from FG.constants import PriorityLevel as PL
from FG.constants import EnergyReason as ER
from FG.constants import GamePhase as GP
from func import say
from system.attribute import Attribute

@dataclass
class CombatData:      # 战斗结果数据类
    damage_to_player: int
    damage_to_pc: int
    description: str
@dataclass
class CombatContext:     # 战斗结果上下文
    """技能执行上下文（用于优先级规则）"""
    player_skill: SkillData | None
    pc_skill: SkillData | None
    skip_damage: bool = False      # 是否跳过伤害结算
    player_damage: int = 0         # 玩家已受伤的伤害值
    pc_damage: int = 0             # PC已受伤的伤害值
    # result_log: list[str] = None

    def __post_init__(self):
        self.result_log = []

class Combat:  # 战斗系统 
    def __init__(self, game: Game):
        self.game = game
        self.attribute = game.attribute

    def execute_turn(self, player_input: str, defense_level: str | None) -> CombatData:   # 执行一个战斗回合
        try:
            self._phase_prepare()
            player_skill = self._phase_player_action(player_input, defense_level)
            pc_skill = self._phase_pc_action()
            return self._phase_resolve(player_skill, pc_skill, defense_level)
        except Exception as e:
            print(f"[战斗系统错误] {e}")
            return CombatData(0, 0, "战斗出现异常")
    
    def judge(self, player_skill_name: str, pc_skill_name: str) -> CombatData: # 判断
        """
        纯计算服务：按优先级顺序执行双方技能，返回战斗结果
        不直接修改状态，只负责判断
        """
        # 1. 获取技能元数据
        player_skill = self.game.get_skill(player_skill_name)
        pc_skill = self.game.get_skill(pc_skill_name)
        
        # 2. 构建执行上下文
        context = CombatContext(player_skill=player_skill, pc_skill=pc_skill)
        
        # 3. 按优先级排序（P1优先，同层按priority数字，玩家优先于PC）
        # 格式：(技能, 归属方) 用于后续日志记录
        skills_to_execute = sorted(
            [(player_skill, "player"), (pc_skill, "pc")],
            key=lambda x: (
                x[0].priority_level.value,  # 先按层级（P1 < P2）
                x[0].priority,              # 再按优先级数字（越小越前）
                0 if x[1] == "player" else 1  # 最后按归属（玩家优先于PC）
            )
        )
        
        # 4. 依次执行技能效果（修改上下文）
        for skill, owner in skills_to_execute:
            self._execute_skill_effect(skill, owner, context)
        
        # 5. 最终伤害结算
        if not context.skip_damage:
            self.damage_do(context)
        
        # 6. 构建并返回结果
        return self._build_priority_result(context)
   
    def _phase_prepare(self):   # 准备阶段
        say(f"【{GP.PREPARE.value}】",ANIMATION_SPEED)
        self.attribute.energy_do(True, ER.ROUND)
        self.attribute.energy_do(False, ER.ROUND)
        return None
    def _phase_player_action(   # 玩家行动阶段
            self, player_input: str, defense_level: str | None):
        say(f"【{GP.ACTION_PLAYER.value}】",ANIMATION_SPEED)

        # case1: 防御选择
        if defense_level:
            self._execute_defense(defense_level)
            return None
        # case2: 攻击选择
        if player_input:
            self._execute_effect(player_input, "你")
            return player_input # 返回name而不是effect
        # case3：暂无
        return None
    def _phase_pc_action(self): # 对手行动阶段
        say(f"【{GP.ACTION_PC.value}】",ANIMATION_SPEED)

        skill_name = self._choose_pc_skill()
        self._execute_effect(skill_name, "对手")
        return skill_name # 返回name而不是effect
    def _phase_resolve(self,    # 结算阶段
        player_skill_name, pc_skill_name, defense_level: str | None) -> CombatData:
        say(f"【{GP.RESOLVE.value}】",ANIMATION_SPEED)

        if defense_level:
            damage = self.damage_calculate(
            attacker_skill_name=pc_skill_name,  # PC攻击
            is_countered=False,                 # 防御回合无克制
            defense_level=defense_level         # 玩家防御等级
        )
            self.game.attribute.damage_take(True, damage)
            return self._build_defense_result(damage)
        else:
            return self.judge(player_skill_name, pc_skill_name)

    def _execute_effect(self, skill_name: str, subject: str):   # 技能效果
        print(subject, end="")
        print(self.game.get_skill(skill_name).effect) 
        sleep(1.5 * ANIMATION_SPEED)

    def _execute_defense(self, defense_level: str):             # 防御效果
        name = f"{defense_level}防御".replace("lv1", "基础").replace("lv2", "进阶")
        print("你", end="")
        print(self.game.get_skill(name).effect) 
        self.attribute.energy_do(True, EnergyReason.DEFENSE_TURN)
        sleep(1.5 * ANIMATION_SPEED)

    def _build_defense_result(self, damage: int) -> CombatData: # 防御结果构建
        names = {'lv1': '基础防御', 'lv2': '进阶防御'}
        desc = f"你全力防御【{names.get(self.attribute.defense_level, '')}】，受到{damage}点伤害"
        return CombatData(damage, 0, desc)
    
    def _choose_pc_skill(self) -> str:                          # pc技能选择逻辑
        current_hp = self.attribute.hp2
        max_hp = getattr(self.attribute, 'hp2_top', 100)
        hp_percentage = current_hp / max_hp

        # 血量高于50%，随机选择lv1攻击技能
        if hp_percentage > 0.5:
            return self._get_random_attack_skill_by_level("lv1")
        if hp_percentage > 0.25:
            return self._get_random_attack_skill_by_level("lv2")
        else:
            # 留余
            return self._get_random_attack_skill_by_level("lv2")   # 当前默认用lv2

    def _get_random_attack_skill_by_level(self, target_level: str) -> str:  # 在指定等级中随机选1个攻击技能
        """基于基础接口构建：在指定等级中随机选1个攻击技能"""
        # 获取所有技能名称
        all_skill_names = list(self.game._skill_cache.keys())
        
        # 过滤出指定等级的攻击技能
        attack_skills = [
            name for name in all_skill_names
            if (self.game.get_skill(name).category == "attack" and 
                self.game.get_skill(name).level == target_level)
        ]
        
        if attack_skills:
            return random.choice(attack_skills)
        
        # 保底机制
        print(f"[警告] 等级 '{target_level}' 没有找到攻击技能，使用默认技能")
        return "基础拳"
    
    def _execute_skill_effect(self, skill: SkillData, owner: str, context: CombatContext):  # 战斗中技能效果的执行
        """在上下文中执行单个技能的效果"""
        
        # 执行技能效果（调用现有的effect函数）
        # 注意：现有effect不接受参数，所以暂时不改变effect签名
        # 后续可扩展为 effect(context)
        
        # 记录日志
        context.result_log.append(f"[{'玩家' if owner == 'player' else '对手'}] {skill.name}")
        
        # 根据技能类型影响上下文
        if skill.category == "defense":
            # 防御效果：标记跳过伤害
            context.skip_damage = True
            context.result_log.append(" → 防御姿态生效")
        elif skill.category == "attack":
            # 攻击效果：如果已标记防御，记录被格挡
            if context.skip_damage:
                context.result_log.append(" → 攻击被防御格挡")
            else:
                context.result_log.append(" → 攻击准备就绪")
        
        sleep(1.5 * ANIMATION_SPEED)

    def damage_do(self, context: CombatContext):    # 战斗中伤害的计算和应用
        """根据上下文计算最终伤害"""
        # 判断克制关系（使用 type 字段）
        player_type = context.player_skill.type if context.player_skill else ""
        pc_type = context.pc_skill.type if context.pc_skill else ""
        
        player_countered = self.game.beats.get(player_type) == pc_type if player_type else False
        pc_countered = self.game.beats.get(pc_type) == player_type if pc_type else False
        
        # 计算伤害（防御已在前面处理，这里不传入defense_level）
        context.player_damage = self.damage_calculate(
            context.player_skill.name, None, player_countered
        )
        context.pc_damage = self.damage_calculate(
            context.pc_skill.name, None, pc_countered
        )
        
        # 应用伤害（状态修改）
        self.game.attribute.damage_take(True, context.player_damage)
        self.game.attribute.damage_take(False, context.pc_damage)
    def damage_calculate(   # 伤害计算
            self, 
            attacker_skill: str | None,      # 攻击方技能名（防御回合为None）
            defender_level: str | None,      # 防御方等级（'lv1', 'lv2' 或 None）
            is_countered: bool               # 是否被克制
        ) -> int:

        # 1. 获取基础伤害（防御回合用默认进阶/基础伤害）
        if attacker_skill is None:
            # 防御回合：无玩家攻击，用防御等级反推
            # 默认伤害 = config.json中数值（暂时硬编码，后续可抽离）
            base_damage = 25 if defender_level == "lv2" else 10
        else:
            # 正常回合：从技能元数据读取
            base_damage = self.game.get_skill(attacker_skill).damage
        
        # 2. 判断攻击方技能等级
        is_lv2_attack = False
        if attacker_skill:
            is_lv2_attack = self.game.get_skill(attacker_skill).level == "lv2"
        else:
            # 防御回合：根据防御等级反推
            is_lv2_attack = defender_level == "lv2"
        
        # 3. 防御减免（纯逻辑，数值不再硬编码）
        # lv1防御：减伤50%（基础）或50%（进阶）
        # lv2防御：减伤100%（基础）或80%（进阶）
        reduction = 0
        if defender_level == "lv1":
            reduction = base_damage * 0.5  # 统一50%减伤
        elif defender_level == "lv2":
            reduction = base_damage * (1.0 if not is_lv2_attack else 0.5)  # 基础全减，进阶减50%
        
        # 4. 最终伤害（保底1点）
        damage = max(1, int(base_damage - reduction))
        
        # 5. 克制翻倍
        if is_countered:
            damage *= 2
        
        return damage
    
    def _build_priority_result(self, context: CombatContext) -> CombatData:  # 优先级结果构建
        """根据上下文构建最终结果"""
        # 判断胜负（基于是否被防御和伤害值）
        if context.skip_damage:
            result_type = "defense"
            result_text = "你全力防御，化解了攻势！"
            winner = None
        elif context.player_damage == context.pc_damage == 0:
            result_type = "draw"
            result_text = "双方虚招试探，未分胜负！"
            winner = None
        elif context.pc_damage > context.player_damage:
            result_type = "win"
            result_text = "你的攻势更凌厉！"
            winner = "player"
        elif context.pc_damage < context.player_damage:
            result_type = "lose"
            result_text = "对方招式老辣，你落得下风！"
            winner = "pc"
        else:
            result_type = "normal"
            result_text = "双方招式不相上下，难分高下！"
            winner = None
        
        # 能量更新
        if result_type == "draw":
            self.attribute.energy_do(True, EnergyReason.COMBAT_DRAW)
            self.attribute.energy_do(False, EnergyReason.COMBAT_DRAW)
        elif result_type == "win":
            self.attribute.energy_do(True, EnergyReason.COMBAT_WIN)
        elif result_type == "lose":
            self.attribute.energy_do(False, EnergyReason.COMBAT_WIN)
        
        # 构建描述文本
        defense_info = ""
        if self.attribute.defense_level:
            defense_names = {'lv1': '基础防御', 'lv2': '进阶防御'}
            defense_info = f" [你使用了{defense_names.get(self.attribute.defense_level, '')}]"
        
        desc = f"{result_text}{defense_info} (你受到{context.player_damage}点伤害，对方受到{context.pc_damage}点伤害)"
        
        # 调试日志（可注释）
        # print("\n[优先级执行日志]", " → ".join(context.result_log))
        
        return CombatData(context.player_damage, context.pc_damage, desc)
