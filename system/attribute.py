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

    def _energy_delta(self, reason: int | str | Enum) -> int:   # 根据原因获取能量变化值
        # 尝试1：枚举的 .value 属性（最可靠）
        try:
            return int(reason.value)  # 安全转换为整数
        except AttributeError:
            pass  # 不是枚举，继续尝试
        
        # 尝试2：直接是整数（如消耗能量 -cost）
        # 必须放在字符串判断之前，因为字符串也有 .isdigit 方法
        if isinstance(reason, int):
            return reason
        
        # 尝试3：字符串映射（兼容旧代码）
        if isinstance(reason, str):
            try:
                enum_name = reason.upper().replace(' ', '_')
                return EnergyReason[enum_name].value
            except KeyError:
                print(f"[警告] 未知的能量原因字符串: '{reason}'")
                return 0
        
        # 最终失败：无法解析
        print(f"[警告] 无法解析能量变化: {reason} (类型: {type(reason).__name__})")
        return 0
    def energy_do(self, is_player: bool ,reason: EnergyReason | str | int) -> int:   # 战斗中能量的获取
        # 根据原因调整能量,支持三种输入

        delta = self._energy_delta(reason)
        
        current = self.energy_get(is_player)
        new_value = current + delta
        return self.energy_set(is_player, new_value)