import random
from time import sleep
from functools import cmp_to_key

def say(txt, delay=2, end='\n'):  # 模拟说话停顿，增加观感
    print(txt, end=end, flush=True)
    sleep(delay)

class SkillTraverse:   # skills字典的遍历，生成菜单选项options
    def __init__(self, game, category: str):
        self.game = game
        self.category = category
        self.filters = []
        self.sorters = []
    
    def add_filter(self, func):  # 过滤函数
        self.filters.append(func)
        return self
      
    def add_default_sorter(self):  # 按等级数字排序，再按消耗排序 
        self.sorters.append(lambda ctx: (
            str(ctx['level']).replace('lv', ''),
            ctx['data']['cost']
        ))
        return self
    
    def build(self, max_opts=25) -> dict:   # 创建返回字典
        options = {}
        collected = []
        
        # 1. 递归收集所有技能
        def _collect(node, path=(), level=None):
            if isinstance(node, dict):
                if "cost" in node:
                    collected.append({'name': path[-1] if path else "未知技能", 'data': node, 'level': level})
                else:
                    for k, v in node.items():
                        # 传递当前层级名称
                        current_level = k if str(k).startswith('lv') else level
                        _collect(v, path + (k,), current_level)
                
        try:
            category_data = self.game.skills[self.category]
            _collect(category_data)
        except KeyError:
            return {'z': (None, True, None)}  # category不存在时安全返回z': (None, True, None)}  # category不存在时安全返回
                    
        # 2. 应用过滤器
        for f in self.filters:
            collected = [c for c in collected if f(c)]
        
        # 3. 应用排序器
        if self.sorters:
            def combined_sorter(a, b):
                for sorter in self.sorters:
                    result = (sorter(a) > sorter(b)) - (sorter(a) < sorter(b))
                    if result != 0:
                        return result
                return 0
            collected.sort(key=cmp_to_key(combined_sorter))
        
        # 4. 生成选项
        for idx, skill in enumerate(collected[:max_opts]):
            key = chr(ord('a') + idx)
            unlocked = self.game._is_skill_unlocked(skill['name'], True)
            options[key] = (skill['name'], unlocked, skill['data'])
        
        options['z'] = (None, True, None)
        return options

class Game: # 主类
    __slots__ = (
        'menu','attribute', # 内部类的实例化调用
        'count','beats','keywords',   
        'skills',    # 将攻击和防御合并作为技能
        'action',   # 其他动作,为日后其他版本迭代做准备
    )   
    class Menu:         # 内部类菜单系统，负责所有用户交互
        def __init__(self,game):
            self.game = game    # 外部调用
        
        def _render_menu(self, options: dict, title: str):   # 增加菜单选择的复用方法，减少在攻击菜单和防御菜单的重复
            print(f"\n{title}")
            for key, (name, unlocked) in options.items():
                if key == 'z':
                    print(f"[{key}] 返回上级")
                else:
                    status = '' if unlocked else '(未解锁)'
                    print(f" [{key}] {name} {status}")
            return input(">>> ").strip().lower() 

        # def _generate_options(self, category: str): # 动态生成菜单选项
        #         """动态生成菜单选项（从skills提取）"""
        #         options = {}
        #         skill_names = self.game.get_skill(key=category)  # 获取该分类下所有技能名
        #         for idx, name in enumerate(skill_names):
        #             key = chr(ord('a') + idx)
        #             unlocked = self.game._is_skill_unlocked(name, True)
        #             options[key] = (name, unlocked)
        #         options['z'] = (None, True)
        #         return options

        def menu_main(self):    # 主菜单
            print("\n【回合开始】你略加思索,决定:")
            print("  [a] 攻击")
            print("  [b] 防御")
            print("  [h] 帮助")
            print("  [q] 逃跑")
            return input(">>> ").strip().lower()

        def menu_attack(self):  # 攻击菜单
            options = {
                "a": ("基础拳", True),
                "b": ("基础剑", True),
                "c": ("基础刀", True),
                "d": ("进阶拳", self.game.attribute.energy_get(True) >= 5),
                "e": ("进阶剑", self.game.attribute.energy_get(True) >= 5),
                "f": ("进阶刀", self.game.attribute.energy_get(True) >= 5),
                "z": (None, True)  # 返回上级
            }
            #显示菜单
            choice = self._render_menu(options,"选择你的攻击招式")
            
            #处理选项
            # 分支1：返回上级
            if choice == 'z':
                return None
            
            # 分支2：无效输入
            if choice not in options:
                print("该招式未习得，你思虑再三决定重新出招。")
                return self.menu_attack()
            
            # 分支3：有效选择
            name, unlocked = options[choice]
            if not unlocked:
                say("对方摇了摇头：'阁下功力尚浅，尚未领悟此招。'")
                return self.menu_attack()  # 重新选择
            
            # 查询消耗
            cost = self.game.get_skill_cost(name)
            if self.game.attribute.energy_get(True) < cost:
                say(f"能量不足{cost}点，无法施展此招！")
                return self.menu_attack()
            # 分支4：唯一返回
            return name

        def menu_defense(self): # 防御菜单
            options = {
                "a": ("基础防御", True),
                "b": ("进阶防御", self.game.attribute.energy_get(True) >= 5),
                "z": (None, True)  # 返回上级
            }
            #显示菜单
            choice = self._render_menu(options,"选择你的防御方式")

            #处理选项
            # 分支1：返回上级
            if choice == 'z':
                return None
            
            # 分支2：无效输入
            if choice not in options:
                print("该招式未习得，你思虑再三决定重新出招。")
                return self.menu_defense()
            
            # 分支3：有效选择
            name, unlocked = options[choice]
            if not unlocked:
                say("对方摇了摇头：'阁下功力尚浅，尚未领悟此招。'")
                return self.menu_defense()  # 重新选择
            
            # 查询消耗
            cost = self.game.get_skill_cost(name)
            if self.game.attribute.energy_get(True) < cost:
                say(f"能量不足{cost}点，无法施展此招！")
                return self.menu_defense()
            # 分支4：唯一返回
             # 返回防御等级标识
            return 'lv1' if name == "基础防御" else 'lv2'
        
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

    def __init__(self): # 大类Game中变量的声明
        self.skills = { # [category][level][skill_name][``]
            "attack": {
                "lv1": {
                    "基础拳": {"cost": 0, "damage": 10, "effect": lambda: print("挥出一拳，拳风袭面门。")},
                    "基础剑": {"cost": 0, "damage": 10, "effect": lambda: print("刺出一剑，刺向薄弱处。")},
                    "基础刀": {"cost": 0, "damage": 10, "effect": lambda: print("砍出一刀，劈向脑门。")},
                },
                "lv2": {
                    "进阶拳": {"cost": 5, "damage": 25, "cooldown": 3, "effect": lambda: print("负手而立，倏然挥出一拳，气动如龙！")},
                    "进阶剑": {"cost": 5, "damage": 25, "cooldown": 3, "effect": lambda: print("躬身、出剑，此世间绝无这么快的剑！")},
                    "进阶刀": {"cost": 5, "damage": 25, "cooldown": 3, "effect": lambda: print("高高跃起，蓄力下劈。此刀势无可披靡！")},
                },
            },
            "defense": {
                "lv1": {
                    "基础防御": {"cost": 0, "effect": lambda: print("气沉丹田,运转自身内力。")},
                },
                "lv2": {
                    "进阶防御": {"cost": 5, "effect": lambda: print("吐纳间蕴含天地之力,似乎没有事物可以伤害自身一毫了。")},
                },
            },
        }
        self.beats = {"拳": "剑", "剑": "刀", "刀": "拳"}
        self.keywords ={"拳","剑","刀"} #
        self.count = 0
        self.menu = self.Menu(self) 
        self.attribute = self.Attribute(self)
        
    def react(self, text: str): # 提取技能关键字来对应招式克制
        if not text:  # 处理None和空字符串
            return None
        for i in self.keywords:
            if i in text:
                return i
        return None 
    
    def action_by_key(self, key: str, action: str = False):  # 用于从关键字中提取技能
            pool = self.get_skill(key = action)
            for name in pool:
                if key in name:
                    return name
            return None
   
    def calculate_damage(   # 伤害计算
            self, skill_attack ,lv_defense ,is_countered
    ):
        # 判断是否为进阶攻击
        is_lv2_attack = skill_attack in self.attack2 if skill_attack else False

        # 基础伤害
        base_damage = 25 if is_lv2_attack else 10
        # 防御减免
        reduction = 0

        # lv1防御：基础减5，进阶减10
        if lv_defense == 'lv1':
            reduction = 5 if not is_lv2_attack else 10
        # lv2防御：基础全减，进阶减20
        elif lv_defense == 'lv2':
            reduction = base_damage if not is_lv2_attack else 20
        # 最终伤害,克制则翻倍
        damage = max(0,base_damage - reduction)
        if is_countered:
            damage *=2
        return damage

    def apply_damage(self, damage_to_pc, damage_to_player): # 应用伤害
        self.attribute.hp2 -= damage_to_pc
        if self.attribute.hp2 < 0:
            self.attribute.hp2 = 0
            
        self.attribute.hp1 -= damage_to_player
        if self.attribute.hp1 < 0:
            self.attribute.hp1 = 0
    
    def is_alive(self, is_player):  # 胜负判定 
        return self.attribute.hp1 > 0 if is_player else self.attribute.hp2 > 0 # 同时为0判玩家为失败

    def get_skill(self, value: str =None, key: str =None) -> dict | list:   # 多层嵌套字典树的遍历查询技能
        """多层嵌套字典灵活查询（支持任意层级键）
    
        Args:
            value: 技能名称（最深层键）
            key: 任意层级的父键
        
        Returns:
            dict: 精确查询返回字典数据
            list: 查询分类/等级返回技能名列表
        """

        # 场景3优先,否则死锁：key + value 联合查询
        if key and value:   
            # 深度优先搜索，找到第一个匹配key的节点
            key_node = self._find_node(self.skills, key)
            if not key_node:
                raise KeyError(f"键 '{key}' 未找到")
            
            # 在key的子树中搜索value
            result = self._find_node(key_node, value, return_parent=False)
            if not result:
                raise KeyError(f"在键 '{key}' 下未找到技能 '{value}'")
            return result

        # 场景1：仅value（全库搜索）
        if value:
            result = self._find_node(self.skills, value, return_parent=False)
            if not result:
                raise KeyError(f"技能 '{value}' 未定义")
            return result
        # 场景2：仅key（返回该键下的所有技能名）
        if key:
            key_node = self._find_node(self.skills, key)
            if not key_node:
                raise KeyError(f"键 '{key}' 未找到")
            
            # 如果找到的是技能字典（第三层），直接返回
            if "cost" in key_node:
                return key_node
            
            # 如果找到的是分类或等级字典，收集其下所有技能名
            return key_node  

        # 边界：返回全库所有技能名
        return self._collect_skill_names(self.skills)
    
    def _find_node(self, node: dict, target: str, return_parent: bool = True) -> dict | None:   # 深度优先搜索（DFS），可返回父节点或值
        """辅助：在嵌套字典中搜索键，可返回父节点或值"""
        if not isinstance(node, dict):
            return None
        
        if target in node:
            return node if return_parent else node[target]
        
        for child in node.values():
            if isinstance(child, dict):
                result = self._find_node(child, target, return_parent)
                if result:
                    return result
        return None

    def _collect_skill_names(self, node: dict) -> list: # 收集嵌套字典中所有技能名（第三层键）
        """辅助：收集嵌套字典中所有技能名（第三层键）"""
        names = []
        if not isinstance(node, dict):
            return names
        
        # 检查当前层级的值是否为技能字典（有cost字段）
        for name, data in node.items():
            if isinstance(data, dict) and "cost" in data:
                names.append(name)
            elif isinstance(data, dict):
                names.extend(self._collect_skill_names(data))
        
        return names

    def get_skill_cost(self, name: str) -> int: # 查询技能消耗
        """查询技能消耗"""
        return self.get_skill(name)["cost"]

    def get_skill_damage(self, name: str) -> int:   # 查询技能伤害
        """查询技能伤害"""
        return self.get_skill(name).get("damage", 0)

    def _is_skill_unlocked(self, name: str, is_player: bool) -> bool:   # 判断技能是否解锁
        """判断技能是否解锁（基础技能永解锁，进阶需能量）"""
        # 通过技能名称反查其等级
        skill_data = self.get_skill(name)
        # 如果技能有cooldown字段，说明是lv2
        return "cooldown" not in skill_data or self.attribute.energy_get(is_player) >= 5

    def judge(self, player: str, pc: str):  # 判断

        # 接受完整技能名并解析关键字
        player = self.react(player)
        pc = self.react(pc)

        # 判断克制关系
        player_countered = self.beats[player] == pc
        pc_countered = self.beats[pc] == player
        
        # 是否使用进阶招式
        player_lv2 = self.attribute.energy_get(True) >= 5
        pc_lv2 = self.attribute.energy_get(False) >= 5

        # 计算伤害
        damage_to_pc = self.calculate_damage(player_lv2, None, player_countered)
        damage_to_player = self.calculate_damage(pc_lv2, self.attribute.defense_level, pc_countered)
        
        # 应用伤害
        self.apply_damage(damage_to_pc, damage_to_player)
        
        # 更新分数
        if player == pc:
            self.attribute.energy_do(True, 'combat_draw')   # 玩家+3
            self.attribute.energy_do(False, 'combat_draw')  # PC+3
            result =  "旗鼓相当，不分胜负！"
        elif self.beats[player] == pc:
            self.attribute.energy_do(True, 'combat_win')
            result =  "你更胜一筹，占得先机！"
        else:
            self.attribute.energy_do(False, 'combat_win')
            result = "对方招式克制，你落得下风！"
       
        # 受击判断
        defense_names = {'lv1': '基础防御', 'lv2': '进阶防御'}
        defense_info = f" [你使用了{defense_names.get(self.attribute.defense_level, '')}]" if self.attribute.defense_level else "" 
        return f"{result}{defense_info} (你受到{damage_to_player}点伤害，对方受到{damage_to_pc}点伤害)"
    
    def fight(self, player_skill: str): # 回合制战斗
        # 明确区分防御和攻击路径
        # is_defense_turn = self.attribute.defense_level is not None
        player = self.react(player_skill)
        self.attribute.energy_do(True, 'round')
        self.attribute.energy_do(False, 'round')

        # 玩家防御
        if self.attribute.defense_level:
            def_dict = self.defense2 if self.attribute.defense_level == 'lv2' else self.defense1
            def_name = "进阶防御" if self.attribute.defense_level == 'lv2' else "基础防御"
            print("你", end="")
            def_dict[def_name]()  # 修复：使用正确的键名
            sleep(1.5)
            player_skill = None  # 执行防御后不攻击
            #防御回合获得基础能量
            self.attribute.energy_do(True, 'defense_turn')  

        # 玩家攻击（防御回合跳过）
        if player_skill:
            print("你", end="")
            attack_dict = self.attack2 if "进阶" in player_skill else self.attack1
            attack_dict[player_skill]()
            sleep(1.5) 

        # 电脑
        pc = random.choice(list(self.keywords))
        pc_lv2 = self.attribute.energy_get(False) >= 5
        pc_skill = self.action_by_key(pc, self.attribute.energy_get(False) >= 5)
        print("对方", end="")
        (self.attack2 if self.attribute.energy_get(False) >= 5 else self.attack1)[pc_skill]()
        sleep(1.5)

        # 判定并显示伤害（修复：防御回合不调用judge）
        if self.attribute.defense_level:
            # 防御回合，单独处理伤害计算
            pc_lv2 = self.attribute.energy_get(False) >= 5
            damage_to_player = self.calculate_damage(pc_lv2, self.attribute.defense_level, False)
            self.attribute.hp1 -= damage_to_player
            if self.attribute.hp1 < 0:
                self.attribute.hp1 = 0
            defense_names = {'lv1': 'lv1防御', 'lv2': 'lv2防御'}
            defense_info = f" [你使用了{defense_names.get(self.attribute.defense_level, '')}]" if self.attribute.defense_level else ""
            say(f"你全力防御{defense_info}，受到{damage_to_player}点伤害")
        else:
            # 正常攻击回合
            print(self.judge(player, pc))

        sleep(2)
        print("-" * 30)
        return True

    def main(self): # 主循环
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

            self.count +=1
            print(f"第{self.count}回合")
            # self.attribute.defense_level = None # 重置防御等级

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
        game = Game()
        game.main()
