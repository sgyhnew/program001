from enum import Enum

class EnergyReason(Enum):   # 能量变化事件
    ROUND = 1         # 每回合开始
    COMBAT_WIN = 3    # 胜利
    COMBAT_DRAW = 1   # 平局
    DEFENSE_TURN = 2  # 防御回合

class GamePhase(Enum):      # 游戏阶段
    PREPARE =        "准备阶段"    
    ACTION_PLAYER =  "玩家行动阶段"
    ACTION_PC =      "对手行动阶段"
    RESOLVE =        "结算阶段"

class SkillLevel(Enum):     # 技能等级
    LV1 = "lv1"
    LV2 = "lv2"

class PriorityLevel(Enum):  # 优先级
    P1 = 1  # 最高
    P2 = 2


BEATS_MAP = {               # 相克关系映射表
    "拳": "剑", 
    "剑": "刀", 
    "刀": "枪",
    "枪": "拳"
}

ANIMATION_SPEED = 1.0  # 动画速度倍率