from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from FG.main import Game
from FG.constants import *
from func import say, load_json, bind_effects
class Attribute:    # 内部类属性系统，负责战斗中状态展示
    def __init__(self,game):
        self.game = game
        

        self.hp1 = 100  # player
        self.hp2 = 100  # pc
        self.hp1_top = 100  # 玩家血量上限
        self.hp2_top = 100  # 对手血量上限
        self._energy_player = 20  # 玩家能量 
        self._energy_pc = 0       # PC能量（FG2.0时移除）
        self.defense_level = None # 防御等级
        self.energy_player_top = 100    # 能量上限
        self.energy_pc_top = 50         # PC能量上限较低，为移除做铺垫

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
        # case1：枚举的 .value 属性
        try:
            return int(reason.value)  # 安全转换为整数
        except AttributeError:
            pass  # 不是枚举，继续尝试
        
        # case2：整数（如消耗能量 -cost）
        # 必须放在字符串判断之前，因为字符串也有 .isdigit 方法
        if isinstance(reason, int):
            return reason
        
        # case3：字符串映射（兼容旧代码）
        if isinstance(reason, str):
            try:
                enum_name = reason.upper().replace(' ', '_')
                return EnergyReason[enum_name].value
            except KeyError:
                print(f"[警告] 未知的能量原因字符串: '{reason}'")
                return 0
        
        # case4：无法解析
        print(f"[警告] 无法解析能量变化: {reason} (类型: {type(reason).__name__})")
        return 0
    def energy_do(self, is_player: bool ,reason: EnergyReason | str | int) -> int:   # 战斗中能量的获取
        # 根据原因调整能量,支持三种输入

        delta = self._energy_delta(reason)
        
        current = self.energy_get(is_player)
        new_value = current + delta
        return self.energy_set(is_player, new_value)
    
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
            base_damage = self.game.get_skill_damage(attacker_skill)
        
        # 2. 判断攻击方技能等级
        is_lv2_attack = False
        if attacker_skill:
            is_lv2_attack = self.game.get_skill_level(attacker_skill) == "lv2"
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
    def damage_take(        # 伤害应用
            self, is_player: bool, amount: int) -> None:    
            hp_attr = 'hp1' if is_player else 'hp2'
            current = getattr(self, hp_attr)
            setattr(self, hp_attr, max(0, current - amount))