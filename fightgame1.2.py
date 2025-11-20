import random
from time import sleep
from time import sleep

def say(txt, delay=2, end='\n'):  # 模拟说话停顿，增加观感
    print(txt, end=end, flush=True)
    sleep(delay)

class FightGame:
    __slots__ = (
        'beats',    
        'score1',
        'score2',
        'menu',     # 新增变量，不再使用户自主输入，而是提供选择菜单
        'keywords', # 关键字提取，不同于上一版本，该改本的关键字提取是提取技能中的文字，因此不与技能挂钩，显示提取，直接命名，不再使player自主输出
        'attack1',  # 基础招式
        'attack2',  # 进阶招式
        'defense',  # 防御,该版本未实装
        'action',   # 其他动作，不同于上一版本，该版本将action中分出attack和defense，保留原action变量来为后续其他动作做铺垫
    )   

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
        self.menu = {
            "a": "基础拳", "b": "基础剑", "c": "基础刀",
            "h": "__help__",      # 特殊标记：帮助 or self.menu.get(choice) == "__help__"
            "q": "__quit__"       # 特殊标记：逃跑
            }

    def react(self, text: str):  # 该版本的招式来自菜单而非player自主输出，因此用法不变，但输入变为菜单中选择的技能名
        for i in self.keywords:
            if i in text:
                return i
        return None 
    
    def action_by_key(self, key: str, advanced: bool = False):  # 新增函数，用于从关键字中提取技能
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

        # 玩家
        print("你", end="")
        (self.attack2 if self.score1 >= 5 else self.attack1)[player_skill]()
        sleep(1.5)

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
            if self.score1 < 5:
                say("对方覆手而立，侧视而笑：'阁下出招吧，拳、剑、刀皆可，若有疑惑，写帮助我自可欣然解答。若是不愿再战，逃走即可！'\n")
            else:
                say("对方全身紧绷，紧紧盯住你一举一动'阁下好身手，我们今日到此为止如何？'\n")

            print("你略加思索，决定：")
            for ch, name in self.menu.items():  # 不再让用户自主输入，而是提供菜单选择
                if ch in {"h", "q"}:    # 特殊标记
                    print(f"  [{ch}] {'帮助' if ch == 'h' else '逃跑'}")
                else:
                    print(f"  [{ch}] {name}")

            choice = input(">>> ").strip().lower()

            # 分发
            if choice == "q":
                say("对方仰天一笑，便不知踪影。")
                break

            if choice == "h":
                say("对方显然很有侠客精神，告诉你：拳克剑、剑克刀、刀克拳。")
                continue

            if choice in self.menu:          # 正常出招
                self.fight(self.menu[choice])
            else:
                print("此招式你尚未习得，思虑再三决定重新出招")

if __name__ == "__main__":
        FightGame().main()