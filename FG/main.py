# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:/e/myprogram/Program/my/program001_FG') 
from constants import *
from constants import EnergyReason as ER
from func import say, load_json, bind_effects

import random
from time import sleep
import json
from functools import lru_cache
from typing import Dict, Any, Callable, Iterator, Tuple
from dataclasses import dataclass
from system.menu import Menu
from system.attribute import Attribute
from system.combat import Combat

@dataclass(frozen=True)  # frozen让对象不可变，可被缓存
class SkillData:    # 技能数据结构
    name: str
    category: str      # 类别
    level: str         # 等级
    cost: int          # 消耗
    effect: Callable[[], None]  # 效果，暂时为输出文本，后期可扩展为其他函数

    damage: int = 0    # 伤害
    cooldown: int = 0  # 冷却

    def __post_init__(self):     # 数据完整性检查，只警告不报错
        if self.category == "attack" and self.damage == 0:
            print(f"警告: 攻击技能 '{self.name}' 缺少伤害值")
        if self.effect is None:
            print(f"警告: 技能 '{self.name}' 缺少effect函数")

class Game:
    __slots__ = (
        'menu','attribute','combat',  # 外部类的调用
        'count','beats','keywords',   # 战斗相关变量
        'skill','action',             # 动作,为日后其他版本迭代做准备
        '_skill_cache'                # 技能缓存，便于使用和查询
    )   

    def __init__(self): # 变量的声明和方法的使用
        self.skill = bind_effects(load_json('data/skill.json'))
        self.beats = BEATS_MAP
        self.keywords = KEYWORD_SYNONYMS
        self.count = 0

        self.menu = Menu(self) 
        self.attribute = Attribute(self)
        self.combat = Combat(self)
        self._skill_cache: Dict[str, SkillData]= {}  #{技能名:(类别，等级，数据字典)}
        self._build_skill_cache()   # 返回值为_skill_cache

    def _traverse_skill(self) -> Iterator[Tuple[str, str, str, Dict[str, Any]]]:   # 生成器迭代遍历
        """生成器：遍历技能树，产出(类别, 等级, 技能名, 数据字典)"""
        for category, levels in self.skill.items():
            for level, skills in levels.items():
                for name, data in skills.items():
                    yield category, level, name, data
    def _build_skill_cache(self) -> None:   # 使用遍历结果构建技能缓存
        self._skill_cache.clear()
        for category, level, name, data in self._traverse_skill():
            self._skill_cache[name] = SkillData(
                name=name,
                category=category,
                level=level,
                cost=data.get("cost", 0),
                damage=data.get("damage", 0),
                effect=data.get("effect", lambda: print("招式效果缺失！"))
            )

    @lru_cache(maxsize=64)  # 缓存查询结果，提升性能
    def get_skill(self, skill_name: str) -> SkillData:     # 查询技能元数据
        """统一查询入口：一次查找，返回完整对象"""
        if skill_name not in self._skill_cache:
            # 提供友好提示，甚至可动态加载新技能
            raise KeyError(f"技能 '{skill_name}' 未定义，请检查 skill.json")
        return self._skill_cache[skill_name]
    def get_skill_name(self, skill_name: str) -> str:       # 查询技能名称
        return self.get_skill(skill_name).name
    def get_skill_cost(self, skill_name: str) -> int:       # 查询技能消耗
        return self.get_skill(skill_name).cost
    def get_skill_level(self, skill_name: str) -> str:      # 查询技能等级
        return self.get_skill(skill_name).level
    def get_skill_category(self, skill_name: str) -> str:   # 查询技能类别
        return self.get_skill(skill_name).category
    def get_skill_damage(self, skill_name: str) -> int:     # 查询技能伤害
        return self.get_skill(skill_name).damage
    def get_skill_effect(self, skill_name: str) -> Callable[[], None]:  # 查询技能效果
        return self.get_skill(skill_name).effect
    
    def react(self, text: str): # 提取技能关键字来对应招式克制
        if not text:  # 处理None和空字符串
            return None
        for synonym, standard in self.keywords.items(): # 查找同义词对应的标准关键字
            if synonym in text:
                return standard
        return None 
    
    def action_by_key(self, key: str, lv2: bool = False) -> str | None:  # 根据关键字和等级选择招式
        level = "lv2" if lv2 else "lv1"

        # 防御性检查：技能结构是否存在
        if "attack" not in self.skill or level not in self.skill["attack"]:
            print(f"[错误] 技能结构异常: attack={self.skill.get('attack')} level={level}")
            return None
        
        # 遍历查找包含key的技能名
        for skill_name in self.skill["attack"][level]:
            if key in skill_name:  
                return skill_name
        return None
        
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
            base_damage = self.get_skill_damage(attacker_skill)
        
        # 2. 判断攻击方技能等级
        is_lv2_attack = False
        if attacker_skill:
            is_lv2_attack = self.get_skill_level(attacker_skill) == "lv2"
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
    def damage_apply(self, damage_to_pc, damage_to_player): # 应用伤害
        self.attribute.hp2 -= damage_to_pc
        if self.attribute.hp2 < 0:
            self.attribute.hp2 = 0
            
        self.attribute.hp1 -= damage_to_player
        if self.attribute.hp1 < 0:
            self.attribute.hp1 = 0
    
    def is_alive(self, is_player):  # 胜负判定 同时为0判玩家为失败
        return self.attribute.hp1 > 0 if is_player else self.attribute.hp2 > 0

    def judge(self, player: str, pc: str):  # 判断

        # 判断克制关系
        player_countered = self.beats[player] == pc
        pc_countered = self.beats[pc] == player
        
        # 是否使用进阶招式
        player_lv2 = self.attribute.energy_get(True) >= 5
        pc_lv2 = self.attribute.energy_get(False) >= 5
        
        # 根据关键字和等级反查具体技能名称
        player_skill = self.action_by_key(player, player_lv2)
        pc_skill = self.action_by_key(pc, pc_lv2)

        # 计算伤害
        damage_to_pc = self.damage_calculate(player_skill, None, player_countered)
        damage_to_player = self.damage_calculate(pc_skill, self.attribute.defense_level, pc_countered)
        
        # 应用伤害
        self.damage_apply(damage_to_pc, damage_to_player)
        
        # 更新分数
        if player == pc:
            self.attribute.energy_do(True, ER.COMBAT_DRAW)   # 玩家+1
            self.attribute.energy_do(False, ER.COMBAT_DRAW)  # PC+1
            result =  "旗鼓相当，不分胜负！"
        elif self.beats[player] == pc:
            self.attribute.energy_do(True, ER.COMBAT_WIN)
            result =  "你更胜一筹，占得先机！"
        else:
            self.attribute.energy_do(False, ER.COMBAT_WIN)
            result = "对方招式克制，你落得下风！"
       
        # 受击判断
        defense_names = {'lv1': '基础防御', 'lv2': '进阶防御'}
        defense_info = f" [你使用了{defense_names.get(self.attribute.defense_level, '')}]" if self.attribute.defense_level else "" 
        return f"{result}{defense_info} (你受到{damage_to_player}点伤害，对方受到{damage_to_pc}点伤害)"
    
    def fight(self, player_skill: str): # 回合制战斗
  
        """Game类只负责调用战斗系统和处理结果"""
        result = self.combat.execute_turn(player_skill, self.attribute.defense_level)
        
        # 根据结果触发额外逻辑（如重伤提示）
        if result.damage_to_player > 20:
            say("这一击让你气血翻涌！")
        
        # 显示结果
        print(result.description)
        return True
          # # 明确区分防御和攻击路径
        # # is_defense_turn = self.attribute.defense_level is not None

        # # 回合开始
        # player = self.react(player_skill)
        # self.attribute.energy_do(True, ER.ROUND)
        # self.attribute.energy_do(False, ER.ROUND)

        # # case1：玩家防御
        # if self.attribute.defense_level:
        #     def_name = "进阶防御" if self.attribute.defense_level == 'lv2' else "基础防御"
        #     print("你", end="")
        #     self.get_skill_effect(def_name)()
        #     sleep(1.5)
        #     player_skill = None  # 执行防御后不攻击
        #     #防御回合获得基础能量
        #     self.attribute.energy_do(True, ER.DEFENSE_TURN)  

        # # case2：玩家攻击（防御回合跳过）
        # if player_skill:
        #     print("你", end="")
        #     self.get_skill_effect(player_skill)()
        #     sleep(1.5) 

        # # case3：电脑
        # standard_keywords = set(self.keywords.values())
        # pc = random.choice(list(standard_keywords))
        # pc_lv2 = self.attribute.energy_get(False) >= 5
        # pc_skill = self.action_by_key(pc, pc_lv2)
        # print("对方", end="")
        # self.get_skill_effect(pc_skill)()
        # sleep(1.5)

        # # 判定并显示伤害（修复：防御回合不调用judge）
        # if self.attribute.defense_level:
        #     # 防御回合，单独处理伤害计算
        #     pc_lv2 = self.attribute.energy_get(False) >= 5
        #     damage_to_player = self.damage_calculate(pc_skill, self.attribute.defense_level, False)
        #     self.attribute.hp1 -= damage_to_player
        #     if self.attribute.hp1 < 0:
        #         self.attribute.hp1 = 0
        #     defense_names = {'lv1': 'lv1防御', 'lv2': 'lv2防御'}
        #     defense_info = f" [你使用了{defense_names.get(self.attribute.defense_level, '')}]" if self.attribute.defense_level else ""
        #     say(f"你全力防御{defense_info}，受到{damage_to_player}点伤害")
        # else:
        #     # 正常攻击回合
        #     print(self.judge(player, pc))

        # sleep(2)
        # print("-" * 30)
        # return True
    
    def main(self): # 主程序入口
        while 1:
            # 回合开始时检查胜负
            if not self.is_alive(True):
                say("\n【战斗结束】你重伤倒地，无法继续战斗...")
                print("对方拱手道：'承让了！'")
                break
            if not self.is_alive(False):
                say("\n【战斗结束】对方口吐鲜血，单膝跪地...")
                print("对方喘息道：'阁下武功高强，在下佩服！'")
                break
            
            # 进入新回合
            self.count +=1
            print(f"第{self.count}回合")

            # 准备阶段
            self.attribute.defense_level = None # 重置防御等级


            if self.attribute.hp2 > 50:
                say("对方覆手而立，侧视而笑：'阁下出招吧，拳、剑、刀皆可，若有疑惑我自可欣然解答。若是不愿再战，逃走即可！'\n")
            else:
                say("对方全身紧绷，紧紧盯住你一举一动'阁下好身手，我们今日到此为止如何？'\n")
            self.attribute.attribute_desc()   # 展示血量
            action = self.menu.menu_main()  # 展示菜单

            if action == 'q':
                say("对方仰天一笑，一个闪身便不知踪影")
                break
            if action == 'h':
                say("对方显然很有侠客精神，叮嘱你拳可剑、剑可刀、刀可拳，随着招式的熟练可以释放更具威力的招式。")
                continue
            if action == 'a':
                # 进入攻击菜单
                skill = self.menu.menu_attack()
                if skill:
                    cost = self.get_skill_cost(skill)  # 动态查询
                    self.attribute.energy_do(True,-cost)  # 自动扣除
                    self.fight(skill)
                continue
            if action == 'b':
                defense_level = self.menu.menu_defense()
                if defense_level:
                    cost = self.get_skill_cost("进阶防御" if defense_level == 'lv2' else "基础防御")
                    self.attribute.energy_do(True,-cost)
                    self.attribute.defense_level = defense_level
                    self.fight("")  # 防御回合

            else:
                print("此招式你尚未习得，思虑再三决定重新出招")

if __name__ == "__main__":
        Game().main()