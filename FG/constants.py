from enum import Enum,auto

class GameResult(Enum):     # 游戏结果名词
    ROUND = "round_start"          # 每回合开始
    COMBAT_WIN = "combat_victory"  # 胜利
    COMBAT_DRAW = "combat_draw"    # 平局
    DEFENSE_TURN = "defense_turn"  # 防御回合

class GamePhase(Enum):      # 游戏阶段
    PREPARE =        "准备阶段"    
    ACTION_PLAYER =  "玩家行动阶段"
    ACTION_PC =      "对手行动阶段"
    RESOLVE =        "结算阶段"
class GameMode(Enum):       # 游戏模式
    ADVENTURE  = '冒险模式'
    CHANLLENGE = '挑战模式' 

class MenuAction(Enum):     # 行动菜单
    ATTACK  = auto()
    SKILL   = auto()
    DEFENSE = auto()
    TOOL    = auto() 


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