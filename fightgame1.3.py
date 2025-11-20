import random
from time import sleep

def say(txt, delay=2, end='\n'):  # 模拟说话停顿，增加观感
    print(txt, end=end, flush=True)
    sleep(delay)

class Fight:
    __slots__ = (
        'count','beats','menu','keywords', 
        'score1','score2',   
        'attack1','attack2',  
        'defense',  # 防御,该版本未实装
        'action',   # 其他动作
    )   
    class Menu: # 新增内部类，专门管理菜单系统，负责所有用户交互
        def __init__(self,game):
            self.game = game    # 外部调用

        def menu_main(self):    #主菜单
            print("\n【回合开始】你略加思索,决定:")
            print("  [a] 攻击")
            print("  [b] 防御（未实装）")
            print("  [h] 帮助")
            print("  [q] 逃跑")
            return input(">>> ").strip().lower()

        def menu_attack(self):  # 攻击菜单
            print("\n你决定选择招式")
            options = {
                "a": ("基础拳", True),
                "b": ("基础剑", True),
                "c": ("基础刀", True),
                "d": ("进阶拳", self.game.score1 >= 5),
                "e": ("进阶剑", self.game.score1 >= 5),
                "f": ("进阶刀", self.game.score1 >= 5),
                "z": (None, True)  # 返回上级
            }
            #显示菜单
            for key,(name,unlocked) in options.items(): 
                if key == 'z':  # 返回
                    print(f"[{key}]返回上级")
                elif isinstance(name,str):
                    status = '' if unlocked else '(未解锁)'
                    print(f" [{key}] {name} {status}")
            choice = input(">>> ").strip().lower()

            # #处理选项
            # if choice == 'z':
            #     return None
            
            # if choice in options:
            #     name,unlocked = options[choice]
            #     if unlocked:
            #         return name
            #     else:
            #         say("对方摇了摇头：'阁下功力尚浅，尚未领悟此招。'")
            #     return self.menu_attack()
            # print("此招式尚未习得，思虑再三决定重新出招")
            # return self.menu_attack()   

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
            
            # 分支4：已解锁 - 唯一正确的返回点
            return name
    
    def __init__(self):
        self.attack1 = {
            "基础拳": lambda: print("挥出一拳，拳风袭面门。"),
            "基础剑": lambda: print("刺出一剑，刺向薄弱处。"),
            "基础刀": lambda: print("砍出一刀，劈向脑门。")            
        }
        self.attack2 = {
            "进阶拳": lambda: print("负手而立，倏然挥出一拳，气动如龙！此拳刚猛而无畏，一拳之威，百鸟溃散！"),
            "进阶剑": lambda: print("躬身、出剑，此世间绝无这么快的剑，也无这么诗意的杀机！"),
            "进阶刀": lambda: print("高高跃起，蓄力下劈。此刀势无可披靡，似若疯魔从天而降，神佛具惊！")
        }
        self.beats = {"拳": "剑", "剑": "刀", "刀": "拳"}
        self.keywords ={"拳","剑","刀"} #
        self.score1 = 0
        self.score2 = 0
        self.count = 0
        self.menu = self.Menu(self) #将内部类Menu实例化

    def react(self, text: str): # 提取技能关键字来对应招式克制
        for i in self.keywords:
            if i in text:
                return i
        return None 
    
    def action_by_key(self, key: str, advanced: bool = False):  # 用于从关键字中提取技能
            pool = self.attack2 if advanced else self.attack1
            for name in pool:
                if key in name:
                    return name
            return None

    def judge(self, player: str, pc: str):
        if player == pc:
            self.score1 += 1
            self.score2 += 1
            return "旗鼓相当，不分胜负！"
        if self.beats[player] == pc:
            self.score1 += 2
            return "你更胜一筹，占得先机！"
        else:
            self.score2 += 2
            return "对方招式克制，你落得下风！"


    def fight(self, player_skill: str):
        player = self.react(player_skill)
        if player is None:
            print("此招式你尚未习得，思虑再三决定重新出招")
            return False

        pc = random.choice(list(self.keywords))
        pc_skill = self.action_by_key(pc, self.score2 >= 5)

        # 修复：根据技能名称判断使用哪个攻击字典 
        # 玩家       
        print("你", end="")
        attack_dict = self.attack2 if "进阶" in player_skill else self.attack1
        attack_dict[player_skill]()
        sleep(1.5)

        # print("你", end="")
        # (self.attack2 if self.score1 >= 5 else self.attack1)[player_skill]()
        # sleep(1.5)

        # 电脑
        print("对方", end="")
        (self.attack2 if self.score2 >= 5 else self.attack1)[pc_skill]()
        sleep(1.5)

        print(self.judge(player, pc))
        sleep(2)
        print("-" * 30)
        return True

    def main(self):
        while 1:
            self.count +=1
            print(f"第{self.count}回合")
            if self.score1 < 5:
                say("对方覆手而立，侧视而笑：'阁下出招吧，拳、剑、刀皆可，若有疑惑，写帮助我自可欣然解答。若是不愿再战，逃走即可！'\n")
            else:
                say("对方全身紧绷，紧紧盯住你一举一动'阁下好身手，我们今日到此为止如何？'\n")

            print("你略加思索，决定：")
            action = self.menu.menu_main()

            if action == 'q':
                say("对方仰天一笑，一个闪身便不知踪影")
                break
            if action == 'h':
                say("对方显然很有侠客精神，叮嘱你拳可剑、剑可刀、刀可拳，随着招式的熟练可以释放更具威力的招式。")
                continue
            if action == 'a':
                # 进入攻击字菜单
                skill = self.menu.menu_attack()
                if skill:
                    self.fight(skill)
                continue
            else:
                print("此招式你尚未习得，思虑再三决定重新出招")

if __name__ == "__main__":
        Fight().main()