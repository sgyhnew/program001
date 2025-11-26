# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:/e/myprogram/Program/my/program001_FG') 
from constants import *
from constants import PriorityLevel as PL
from func import say, load_json

import random
from time import sleep
import json
from functools import lru_cache
from typing import Dict, Any, Callable, Iterator, Tuple
from dataclasses import dataclass

from system.attribute import Attribute
from system.menu import Menu
from system.combat import Combat

@dataclass(frozen=True)  # frozen让对象不可变，可被缓存
class SkillData:    # 技能数据结构
    category: str       # 行动类别
    level: str          # 等级
    name: str           # 技能名称

    cost: int            # 消耗
    priority_level: Enum # 优先级阶级
    priority: int        # 优先级等级
    effect: str          # 效果，暂时为输出文本，后期可扩展为其他函数

    damage: int = 0     # 伤害
    cooldown: int = 0   # 冷却
    type: str  ="其他"  # 技能类型


    def __post_init__(self):     # 数据完整性检查，只警告不报错
        if self.category == "attack":
            if self.damage == 0:
                print(f"警告: 攻击技能 '{self.name}' 缺少伤害值")
            if not self.type:
                print(f"警告: 攻击技能 '{self.name}' 缺少type字段")
        if self.priority_level is None:
            print(f"警告: 技能 '{self.name}' 缺少priority_level字段")
        if self.effect is None:
            print(f"警告: 技能 '{self.name}' 缺少effect函数")
class Game:
    __slots__ = (
        'menu','attribute','combat',  # 外部类的调用
        'count','beats',              # 战斗相关变量
        'skill','action',             # 动作,为日后其他版本迭代做准备
        '_skill_cache'                # 技能缓存，便于使用和查询
    )   
    def __init__(self): # 变量的声明和方法的使用
        self.skill = load_json('data/skill.json')
        self.beats = BEATS_MAP
        self.count = 0

        self.attribute = Attribute(self)
        self.menu = Menu(self)
        self.combat = Combat(self)
        self._skill_cache: Dict[str, SkillData]= {}  #{name: SkillData}
        self._build_skill()   # 返回值为_skill_cache

    def _traverse_skill(self) -> Iterator[Tuple[str, str, str, Dict[str, Any]]]:   # 生成器迭代遍历
        """生成器：遍历技能树，产出(类别, 等级, 技能名, 数据字典)"""
        for category, levels in self.skill.items():
            for level, skills in levels.items():
                for name, data in skills.items():
                    yield category, level, name, data
    def _build_skill(self) -> None:                                                # 使用遍历结果构建技能缓存
        self._skill_cache.clear()
        for category, level, name, data in self._traverse_skill():
            p_level_str = data.get("priority_level", "P2")
            p_level = PL[p_level_str]  # "P2" -> PriorityLevel.P2
            self._skill_cache[name] = SkillData(
                category=category,
                level=level,
                name=name,
                cost=data.get("cost", 0),
                priority_level=p_level,
                priority=data.get("priority", 2),
                effect=data.get("effect", "招式效果缺失！"),
                damage=data.get("damage", 0),
                cooldown=data.get("cooldown", 0),  # 新增
                type=data.get("type", "其他")
        )

    @lru_cache(maxsize=64)  # 缓存查询结果，提升性能
    def get_skill(self, skill_name: str) -> SkillData:      # 查询技能元数据
        """统一查询入口：一次查找，返回完整对象"""
        if skill_name not in self._skill_cache:
            # 提供友好提示，甚至可动态加载新技能
            raise KeyError(f"技能 '{skill_name}' 未定义，请检查 skill.json")
        return self._skill_cache[skill_name]

    def is_alive(self, is_player):  # 胜负判定 同时为0判玩家为失败
        return self.attribute.hp1 > 0 if is_player else self.attribute.hp2 > 0

    def fight(self, player_skill: str): # 回合制战斗
  
        """Game类只负责调用战斗系统和处理结果"""
        result = self.combat.execute_turn(player_skill, self.attribute.defense_level)
        
        # 根据结果触发额外逻辑
        if result.damage_to_player > 20:    # 重伤提示
            say("这一击让你气血翻涌！")
        
        # 显示结果
        say(result.description)
        return True
    
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
            # self.menu.debug_state() # debug
            menu_result = self.menu.run()     # 实例化菜单栈

            if menu_result is None:
                # 正常返回，继续下一回合
                continue

            elif menu_result == '__exit__':  # 退出
                break
            elif isinstance(menu_result, str):
                # 攻击技能选择
                skill_name = menu_result
                try:
                    skill_data = self.get_skill(skill_name)
                    cost = skill_data.cost
                    
                    # 检查能量是否足够
                    if self.attribute.energy_get(True) >= cost:
                        self.attribute.energy_do(True, -cost)
                        self.fight(skill_name)
                    else:
                        say(f"能量不足{cost}点，无法施展{skill_name}！")
                        
                except KeyError:
                    say(f"技能'{skill_name}'数据异常，无法使用")
            elif isinstance(menu_result, int):
                # 防御等级选择
                defense_level = menu_result
                try:
                    # 根据防御等级获取对应的防御技能
                    defense_skill_name = "进阶防御" if defense_level >= 2 else "基础防御"
                    skill_data = self.get_skill(defense_skill_name)
                    cost = skill_data.cost
                    
                    # 检查能量是否足够
                    if self.attribute.energy_get(True) >= cost:
                        self.attribute.energy_do(True, -cost)
                        self.attribute.defense_level = defense_level
                        self.fight("")  # 防御回合
                    else:
                        say(f"能量不足{cost}点，无法进行防御！")
                        
                except KeyError:
                    say("防御技能数据异常")
            else:
                print("此招式你尚未习得，思虑再三决定重新出招")

if __name__ == "__main__":
        Game().main()