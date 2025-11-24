import sys
sys.path.insert(0, r'D:/e/myprogram/Program/my/program001_FG') 
from FG.constants import *
from func import say, load_json, bind_effects
class Attribute:    # 内部类属性系统，负责战斗中状态展示
    def __init__(self,game):
        self.game = game
        self.hp1 = 100  # player
        self.hp2 = 100  # pc
        self._energy_player = 20  # 玩家能量 
        self._energy_pc = 0       # PC能量（FG2.0时移除）
        self.defense_level = None # 防御等级
        self.energy_player_top = 100    # 能量上限
        self.energy_pc_top = 50  # PC能量上限较低，为移除做铺垫

    def attribute_desc(self): # 状态描述
        
        player_energy = self.energy_get(True)
        pc_energy = self.energy_get(False)
        print(f"  ❤️  玩家血量: {self.hp1:>3}/100  |  ⚔️  能量: {player_energy:>2}/{self.energy_player_top}")
        print(f"  💀 对手血量: {self.hp2:>3}/100  |  🛡️  能量: {pc_energy:>2}/{self.energy_pc_top}")
        print(f"{'='*40}")

    def energy_get(self, is_player:bool) -> int: # 能量的调用
        return self._energy_player if is_player else self._energy_pc

    def energy_set(self, is_player:bool, value): # 能量的设置
        attr = '_energy_player' if is_player else '_energy_pc'
        attr_top = 'energy_player_top' if is_player else 'energy_pc_top'
        top = getattr(self,attr_top)
        new_val = max(0,min(value,top))
        setattr(self, attr, new_val)
        return new_val

    def energy_do(self, is_player: bool ,reason: int | str):   # 战斗中能量的获取
        # 结果标识映射表
        REASON = {  
            'round': 1,         # 每回合开始
            'combat_win': 3,    # 战斗胜利
            'combat_draw': 1,   # 平局
            'defense_turn': 2,  # 防御回合
            # 'take_damage': 1,   # 受伤补偿
        }

        # 实际表更量
        delta = (   
            reason
            if isinstance(reason, int) 
            else REASON.get(reason, 0)
        )   

        # 应用变更并返回新值
        return self.energy_set(is_player, self.energy_get(is_player) + delta)
