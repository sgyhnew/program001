from enum import Enum

class EnergyReason(Enum):   # 能量变化原因
    ROUND = 1         # 每回合开始
    COMBAT_WIN = 3    # 胜利
    COMBAT_DRAW = 1   # 平局
    DEFENSE_TURN = 2  # 防御回合

class GamePhase(Enum):      # 游戏阶段
    PREPARE = "准备阶段"    
    ACTION = "行动阶段"
    RESOLVE = "结算阶段"

class SkillLevel(Enum):     # 技能等级
    BASIC = "lv1"
    ADVANCED = "lv2"


KEYWORD_SYNONYMS = {        # 关键字同义词映射，所有同义词均映射到**标准关键字**
    "拳": "拳",     # 拳法相关
    "掌": "拳", 
    "指": "拳",  
    
    "剑": "剑",     # 剑术相关
    "刺": "剑",
    
    "刀": "刀",     # 刀法相关
    "斩": "刀",
    
    # "枪": "枪",     # 枪术相关
    # "棍": "枪",
    # "棒": "枪"
}

BEATS_MAP = {               # 相克关系映射表
    "拳": "剑", 
    "剑": "刀", 
    "刀": "拳",
    # "枪": "拳" 
}