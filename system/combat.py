# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
sys.path.insert(0, r'D:/e/myprogram') 

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable
import random
from time import sleep

from FG.constants import *
from FG.constants import EnergyReason as ER
from FG.constants import GamePhase as GP
if TYPE_CHECKING:
    from FG.main import Game
from .attribute import Attribute
from func import say

@dataclass
class CombatResult:  # 战斗结果数据类
    damage_to_player: int
    damage_to_pc: int
    description: str

class Combat:  # 战斗系统 
    def __init__(self, game: Game):
        self.game = game
        self.attribute = Attribute(game)  

    def execute_turn(self, player_input: str, defense_level: str | None) -> CombatResult:   # 执行一个战斗回合
        try:
            self._phase_prepare()
            player_skill = self._phase_player_action(player_input, defense_level)
            pc_skill = self._phase_pc_action()
            return self._phase_resolve(player_skill, pc_skill, defense_level)
        except Exception as e:
            print(f"[战斗系统错误] {e}")
            return CombatResult(0, 0, "战斗出现异常")
    
    def _phase_prepare(self):   # 准备阶段
        print(f"{GP.PREPARE.value}")
        self.attribute.energy_do(True, ER.ROUND)
        self.attribute.energy_do(False, ER.ROUND)
        sleep(0.5)
        return None
    def _phase_player_action(   # 玩家行动阶段
            self, player_input: str, defense_level: str | None):
        print(f"{GP.ACTION_PLAYER.value}")

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
        print(f"{GP.ACTION_PC.value}")

        skill_name = self._choose_pc_skill()
        self._execute_effect(skill_name, "对手")
        return skill_name # 返回name而不是effect
    def _phase_resolve(self,    # 结算阶段
        player_skill_name, pc_skill_name, defense_level: str | None) -> CombatResult:
        print(f"{GP.RESOLVE.value}")

        if defense_level:
            damage = self.game.damage_calculate(
                pc_skill_name, defense_level, False
            )
            self.attribute.take_damage(True, damage)
            return self._build_defense_result(damage)
        else:
            return self._build_combat_result(player_skill_name, pc_skill_name)

    def _execute_effect(self, skill_name: str, subject: str):   # 技能效果
        print(subject, end="")
        self.game.get_skill_effect(skill_name)()
        sleep(1.5 * ANIMATION_SPEED)

    def _execute_defense(self, defense_level: str):             # 防御效果
        name = f"{defense_level}防御".replace("lv1", "基础").replace("lv2", "进阶")
        print("你", end="")
        self.game.get_skill_effect(name)()
        self.attribute.energy_do(True, EnergyReason.DEFENSE_TURN)
        sleep(1.5 * ANIMATION_SPEED)

    def _choose_pc_skill(self) -> str:  # pc技能选择逻辑
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

    def _get_random_attack_skill_by_level(self, target_level: str) -> str:
        """基于基础接口构建：在指定等级中随机选1个攻击技能"""
        # 获取所有技能名称
        all_skill_names = list(self.game._skill_cache.keys())
        
        # 过滤出指定等级的攻击技能
        attack_skills = [
            name for name in all_skill_names
            if (self.game.get_skill_category(name) == "attack" and 
                self.game.get_skill_level(name) == target_level)
        ]
        
        if attack_skills:
            return random.choice(attack_skills)
        
        # 保底机制
        print(f"[警告] 等级 '{target_level}' 没有找到攻击技能，使用默认技能")
        return "基础拳"
    
    def _build_defense_result(self, damage: int) -> CombatResult:
        names = {'lv1': '基础防御', 'lv2': '进阶防御'}
        desc = f"你全力防御【{names.get(self.attribute.defense_level, '')}】，受到{damage}点伤害"
        return CombatResult(damage, 0, desc)

    def _build_combat_result(self, player_skill_name, pc_skill_name) -> CombatResult:
        # 简化版：复用原有judge逻辑
        player = self.game.react(player_skill_name if player_skill_name else None)
        pc = self.game.react(pc_skill_name if pc_skill_name else None)
        
        player_countered = self.game.beats.get(player) == pc if player else False
        pc_countered = self.game.beats.get(pc) == player if player else False
        
        damage_to_pc = self.game.damage_calculate(
            player_skill_name if player_skill_name else None, 
            None, 
            player_countered
        )
        damage_to_player = self.game.damage_calculate(
            pc_skill_name, 
            self.attribute.defense_level, 
            pc_countered
        )
        
        # 应用伤害
        self.attribute.take_damage(False, damage_to_pc)
        self.attribute.take_damage(True, damage_to_player)
        
        # 生成描述文本
        if player == pc:
            self.attribute.energy_do(True, EnergyReason.COMBAT_DRAW)
            self.attribute.energy_do(False, EnergyReason.COMBAT_DRAW)
            result = " 旗鼓相当，不分胜负！"
        elif self.game.beats.get(player) == pc:
            self.attribute.energy_do(True, EnergyReason.COMBAT_WIN)
            result = " 你更胜一筹，占得先机！"
        else:
            self.attribute.energy_do(False, EnergyReason.COMBAT_WIN)
            result = " 对方招式克制，你落得下风！"
        
        defense_info = ""
        if self.attribute.defense_level:
            defense_names = {'lv1': '基础防御', 'lv2': '进阶防御'}
            defense_info = f" [你使用了{defense_names.get(self.attribute.defense_level, '')}]"
        
        desc = f"{result}{defense_info} (你受到{damage_to_player}点伤害，对方受到{damage_to_pc}点伤害)"
        return CombatResult(damage_to_player, damage_to_pc, desc)