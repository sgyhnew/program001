# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:/e/myprogram') 
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable
import random
from time import sleep

from FG.constants import *
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
        self.attribute = game.attribute

    