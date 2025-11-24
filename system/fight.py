# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:/e/myprogram') 
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable
import random
from time import sleep

from FG.constants import *
from FG.constants import EnergyReason as ER
from FG.main import Game
from attribute import Attribute
from func import say

@dataclass
class CombatResult:  # 战斗结果数据类
    damage_to_player: int
    damage_to_pc: int
    description: str

class Fight:  # 战斗系统核心类
    def __init__(self, game):
        self.game = game
        self.attribute = Attribute(game)  # 战斗属性系统实例
        self._phase = GamePhase
        self.reason = ER

    def _phase_prepare(self):   
        print(f"\n{GamePhase.PREPARE.value}")
        self.attribute.energy_do(True, ER.ROUND)
        self.attribute.energy_do(False, ER.ROUND)
        sleep(0.5)
        return None
    def _phase_player_action(self, player_input: str, defense_level: str | None):
        return None
    def _phase_pc_action(self):
        return None
    def _phase_resolve(self, player_skill, pc_skill, defense_level: str | None) -> CombatResult:
        return CombatResult(0, 0, "战斗解析未实现")

    def execute_turn(self, player_input: str, defense_level: str | None) -> CombatResult:
        """执行一个完整回合，返回结果数据"""
        try:
            self._phase_prepare()
            player_skill = self._phase_player_action(player_input, defense_level)
            pc_skill = self._phase_pc_action()
            return self._phase_resolve(player_skill, pc_skill, defense_level)
        except Exception as e:
            print(f"[战斗系统错误] {e}")
            return CombatResult(0, 0, "战斗出现异常")
    