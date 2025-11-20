import random
from time import sleep

def say(txt, delay=2, end='\n'):  # 模拟说话停顿，增加观感
    print(txt, end=end, flush=True)
    sleep(delay)

class Game:
    __slots__ = (
        'menu','attribute', # 内部类的实例化调用
        'count','beats','keywords', 
        'score1','score2',   
        'attack1','attack2',  
        'defense',  # 防御,该版本未实装
        'action',   # 其他动作
    )   
    class Menu: # 新增内部类菜单系统，负责所有用户交互
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
    
    class Attribute:    # 新增内部类属性系统，负责战斗中状态展示
        def __init__(self,game):
            self.game = game
            self.hp1 = 100  # player
            self.hp2 = 100  # pc

        def attribute_hp(self):
            # print(f"\n{'='*35}")
            # print(f"  玩家血量: {self.hp1}/100  |  熟练度: {self.game.score1}")
            # print(f"  对手血量: {self.hp2}/100  |  熟练度: {self.game.score2}")
            # print(f"{'='*35}\n")
            #           
            print(f"\n{'='*40}")
            print(f"  ❤️  玩家血量: {self.hp1:>3}/100  |  ⚔️  熟练度: {self.game.score1:>2}")
            print(f"  💀 对手血量: {self.hp2:>3}/100  |  🛡️  熟练度: {self.game.score2:>2}")
            print(f"{'='*40}\n")

    def __init__(self): # 大类Game中变量的声明
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
        self.menu = self.Menu(self) 
        self.attribute = self.Attribute(self)

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

    def judge(self, player: str, pc: str):  # 判断
        # 判断克制关系
        player_countered = self.beats[player] == pc
        pc_countered = self.beats[pc] == player
        
        # 是否使用进阶招式
        player_advanced = self.score1 >= 5
        pc_advanced = self.score2 >= 5
        
        # 计算伤害
        damage_to_pc = self.calculate_damage(player_advanced, player_countered)
        damage_to_player = self.calculate_damage(pc_advanced, pc_countered)
        
        # 应用伤害
        self.apply_damage(damage_to_pc, damage_to_player)
        
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

    def fight(self, player_skill: str): # 回合制战斗
        player = self.react(player_skill)
        if player is None:
            print("此招式你尚未习得，思虑再三决定重新出招")
            return False

        pc = random.choice(list(self.keywords))
        pc_skill = self.action_by_key(pc, self.score2 >= 5)

        # 玩家       
        print("你", end="")
        attack_dict = self.attack2 if "进阶" in player_skill else self.attack1
        attack_dict[player_skill]()
        sleep(1.5)

        # 电脑
        print("对方", end="")
        (self.attack2 if self.score2 >= 5 else self.attack1)[pc_skill]()
        sleep(1.5)

        # 判定并显示伤害
        print(self.judge(player, pc))
        sleep(2)
        
        print("-" * 30)
        return True

    def calculate_damage(self, is_advanced, is_countered):# 新增：伤害计算（大类负责逻辑）
        base_damage = 25 if is_advanced else 10
        return base_damage * 2 if is_countered else base_damage
    
    def apply_damage(self, damage_to_pc, damage_to_player): # 新增：应用伤害（大类负责逻辑）
        self.attribute.hp2 -= damage_to_pc
        if self.attribute.hp2 < 0:
            self.attribute.hp2 = 0
            
        self.attribute.hp1 -= damage_to_player
        if self.attribute.hp1 < 0:
            self.attribute.hp1 = 0
    
    def is_alive(self, is_player):  # 新增：胜负判定 同时为0判玩家为失败
        return self.attribute.hp1 > 0 if is_player else self.attribute.hp2 > 0

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
            if self.score1 < 5:
                say("对方覆手而立，侧视而笑：'阁下出招吧，拳、剑、刀皆可，若有疑惑，写帮助我自可欣然解答。若是不愿再战，逃走即可！'\n")
            else:
                say("对方全身紧绷，紧紧盯住你一举一动'阁下好身手，我们今日到此为止如何？'\n")
            self.attribute.attribute_hp()   # 展示血量
            action = self.menu.menu_main()  # 展示菜单

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
        Game().main()