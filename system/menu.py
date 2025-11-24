from func import say

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
    