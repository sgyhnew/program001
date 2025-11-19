import random
from time import sleep

_DELAY = 2  # 全局延迟秒数


def say(txt, end='\n'):  # 模拟说话停顿，增加观感
    print(txt, end=end, flush=True)
    sleep(_DELAY)


class FightGame:
    __slots__ = (
        "beats",     # 招式克制关系
        "keywords",  # 关键字提取
        "score1",    # 内置隐形积分1，默认玩家
        "score2",    # 内置隐性积分2，默认电脑
        "actions1",  # 动作1，基础招式
        "actions2",   # 动作2，进阶招式
        # "actions3"   # 动作3，防御招式
    )  # 限定字典，剩内存且好查阅

    def __init__(self):
        self.actions1 = {
            "拳": lambda: print("挥出一拳，拳风袭面门。"),
            "剑": lambda: print("刺出一剑，刺向薄弱处。"),
            "刀": lambda: print("砍出一刀，劈向脑门。")
        }
        self.actions2 = {
            "拳": lambda: print("负手而立，倏然挥出一拳，气动如龙！此拳刚猛而无畏，一拳之威，百鸟溃散！"),
            "剑": lambda: print("躬身、出剑，此世间绝无这么快的剑，也无这么诗意的杀机！"),
            "刀": lambda: print("高高跃起，蓄力下劈。此刀势无可披靡，似若疯魔从天而降，神佛具惊！")
        }
        self.beats = {"拳": "剑", "剑": "刀", "刀": "拳"}
        self.keywords = list(self.actions1.keys())
        self.score1 = 0
        self.score2 = 0

    def react(self, text: str):  # 出招，提取关键字
        for i in self.keywords:
            if i in text:
                return i
        return None

    def judge(self, player: str, pc: str):  # 判定
        if player == pc:
            self.score1 += 1
            self.score2 += 1
            return '你和对方旗鼓相当，不分胜负！'
        if self.beats[player] == pc:
            self.score1 += 2
            return '你更胜一筹，占得先机'
        else:
            self.score2 += 2
            return '对方招式克制，你落得下风'

    def fight(self, player_input: str):  # 对战回合制
        player = self.react(player_input)
        if player is None:
            print("此招你尚未习得，思虑再三决定重新出招")
            return False
        pc = random.choice(self.keywords)

        print(f"你", end="")
        if self.score1 >= 5:
            self.actions2[player]()
            sleep(2)
        else:
            self.actions1[player]()
            sleep(2)

        print(f"对方", end="")
        if self.score2 >= 5:
            self.actions2[pc]()
            sleep(2)
        else:
            self.actions1[pc]()
            sleep(2)

        print(self.judge(player, pc))
        sleep(2)
        print("-"*30)
        return True

    def get_score(self):    # 积分的获得，方便后续其使用
        return self.score1

    def main(self):
        while 1:
            if self.score1 < 5:
                say("对方覆手而立，侧视而笑：'阁下出招吧，拳、剑、刀皆可，若是不愿再战，逃走即可！'\n")
            else:
                say("对方全身紧绷，紧紧盯住你一举一动'阁下好身手，我们今日到此为止如何？'\n")
            a = input("你略加思索，决定：\n")
            if a.lower() == '逃走':
                sleep(2)
                say("对方仰天一笑，便不知踪影。")
                break

            self.fight(a)


if __name__ == "__main__":
    FightGame().main()

'''
#
# end = {
#         1: lambda: print("玩家赢了！"),
#         2: lambda: print("玩家惜败！"),
# }
# actions1 = {
#     "拳": lambda: print("挥拳而出，气动如龙！此拳刚猛而无畏，一拳之威，百鸟溃散！"),
#     "剑": lambda: print("躬身、出剑，此世间绝无这么快的剑，也无这么诗意的杀机！"),
#     "刀": lambda: print("高高跃起，蓄力下劈。此刀势无可披靡，似若疯魔从天而降，神佛具惊！"),
# }
# beats = {"拳": "剑", "剑": "刀", "刀": "拳"}
#
# actions2 = {
#     "压": lambda: print("压制力尚可，可惜破绽百出。"),
#     "进": lambda: print("前进得鲁莽，漏洞明显。"),
#     "退": lambda: print("似退不退，怯弱而无英雄气。"),
#     "拳": lambda: print("拳法虽了得，但不过如此。"),
#     "剑": lambda: print("有剑气无剑心，剑乃百兵之首，你之所用令人贻笑大方。"),
#     "刀": lambda: print("凌乱而无杀气，可惜。"),
# }
# actions3 = {
#     ("赢", "上风", "大破"): lambda: print("你渐入佳境，对方招式你自可一一看破"),
#     ("输", "下风", "失败"): lambda: print("你逐渐力不从心，对方招式千变万化，你自认并非其对手")
# }
'''
