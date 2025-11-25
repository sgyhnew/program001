
from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from FG.main import Game
from func import say, load_json
from typing import Dict, Tuple
from math import ceil
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class MenuData:   # 菜单状态数据
    menu_type: str          # 菜单类型
    select_index: int = 0   # 选择索引
    page: int = 0           # 当前页码
    context: dict = None    # 上下文数据

    def __repr__(self):
        return f"MenuData(type={self.menu_type}, index={self.select_index}, page={self.page}, context={self.context})"

class MenuStack:  # 菜单栈，管理菜单状态
    def __init__(self, game):
        self.game = game
        self.stack : list[MenuData] = [MenuData('main')]  # 菜单栈初始化为空列表
        self.state_cache: Dict[str, MenuData] = {}  # 菜单状态缓存

    def push(self,menu_type: str, context: Dict = None) -> MenuData:   # 入栈
        # 保存当前状态到缓存
        # print(f"[DEBUG] 开始push: {menu_type}, 当前栈深度: {len(self.stack)}")
    
        if self.stack:
            current = self.stack[-1]
            self.state_cache[current.menu_type] = current
        
        # 创建或恢复新状态
        cache_key = f"{menu_type}_{context.get('category', '')}_{context.get('level', '')}" if context else menu_type
        new_state = self.state_cache.get(cache_key) or MenuData(menu_type, 0, 0, context)
        
        self.stack.append(new_state)
        return new_state

    def pop(self) -> MenuData | None:      # 出栈
        if len(self.stack) > 1:
            popped = self.stack.pop()
            # 恢复上一菜单状态（从缓存）
            if self.stack:
                current = self.stack[-1]
                cached = self.state_cache.get(current.menu_type)
                if cached:
                    current.select_index = cached.select_index
                    current.page = cached.page
            return popped
        return None  # 保持在栈底

    def get_current(self) -> MenuData | None:   # 获取当前菜单状态
        if self.stack:
            return self.stack[-1] 
        else: 
            print("当前菜单是空的")
            return None
    def clear(self):    # 清空栈
        self.stack.clear()
        self.state_cache.clear()
    def is_root(self) -> bool:           # 检查是否在根目菜单
        return len(self.stack) ==1

class Menu:       # 菜单系统，负责所有用户交互
    def __init__(self,game):
        self.game = game    # 外部调用
        self.attribute = game.attribute
        self.stack = MenuStack(game)  # 菜单栈
    
    def navigate_to(            # 导航到指定菜单
            self, target_menu: str, context: Dict = None) -> bool:  
        try:
            # print(f"[DEBUG] 导航: {self.get_current_state().menu_type} -> {target_menu}")  # 调试
            # 确保状态栈有效
            if not self.stack.stack:
                self.stack.stack = [MenuData('main')]
            
            # 执行导航
            new_state = self.stack.push(target_menu, context)
            # print(f"[DEBUG] 导航成功，新状态: {new_state}")
            # print(f"[DEBUG] 栈深度: {len(self.stack.stack)}")
            
            return True
        except Exception as e:
            print(f"[DEBUG] 导航失败: {e}")
            return False
    
    def go_back(self) -> bool:  # 返回上一级菜单
        return self.stack.pop() is not None
    
    def get_current_state(self) -> MenuData:    # 获取当前菜单状态
        return self.stack.get_current()
    
    def _update_state_selection(                # 更新当前菜单状态的选择索引
            self, selected_key: str, options: Dict):  
        current_state = self.get_current_state()
        if current_state and selected_key in options:
            # 将选项键转换为索引（如 'a'->0, 'b'->1）
            keys = [k for k in options.keys() if k != 'z']  # 排除返回键
            if selected_key in keys:
                current_state.select_index = keys.index(selected_key)
    def _get_options_keys(                      # 获取选项键列表，排除返回键 'z' 
            self, options: Dict) -> List[str]:   
        return [k for k in options.keys() if k != 'z']

    def _render_menu(           # 分页，渲染菜单，复用
            self, options: Dict[str, Tuple[str, bool, int]], title: str,page: int = 0, show_cost: bool = True) -> str: 
        #options: {key: (name, unlocked, cost)}
        current_state = self.get_current_state()
        if page is None and current_state:
            page = current_state.page
        # 分页
        page_size = 6
        # 分离 'z' 返回键和其他选项
        main_items = [(k, v) for k, v in options.items() if k != 'z']
        # 总页数 = 总项数/6 ，向上取整
        total_pages = ceil(len(main_items) / page_size)

        if page is None:
            page =0
        
        while True:  # 分页循环
            # 更新当前状态页码
            if current_state:
                current_state.page = page
            print(f"\n{title}")
            
            # 计算当前页显示的选项
            start_idx = page * page_size
            end_idx = start_idx + page_size
            page_items = main_items[start_idx:end_idx]
            valid_keys = [k for k, _ in page_items]
            # 渲染当前页选项
            for key, (name, unlocked, cost) in page_items:
                if show_cost:
                    status = f"(未解锁 需{cost}能量)" if not unlocked else f"(消耗{cost}能量)"
                else:
                    status = ''
                print(f" [{key}] {name} {status}")

                # 增强对技能的渲染
                if hasattr(self.game, 'get_skill'):
                    try:
                        skill_data = self.game.get_skill(name)
                        # 显示伤害、冷却等信息
                        damage_info = f"伤害:{skill_data.damage}" if skill_data.damage > 0 else ""
                        cooldown_info = f"冷却:{skill_data.cooldown}" if skill_data.cooldown > 0 else ""
                        effect_info = f"效果:{skill_data.effect[:10]}..." if skill_data.effect else ""
                        
                        extra_info = " ".join(filter(None, [damage_info, cooldown_info, effect_info]))
                        if extra_info:
                            status = f"{status} [{extra_info}]"
                            
                    except KeyError:
                        pass  # 技能数据获取失败，使用基础显示
                
                print(f" [{key}] {name} {status}")
            
            # 渲染底部控制栏
            controls = []
            if page > 0:
                controls.append(" [l] 上一页")
            if page < total_pages - 1:
                controls.append(" [r] 下一页")
            controls.append(" [z] 返回上级")
            
            print("".join(controls))
            print(f" 第 {page + 1}/{total_pages} 页")
            
            # 获取用户输入
            choice = input(">>> ").strip().lower()
            
            # 处理翻页命令
            if choice == 'l' and page > 0:
                page -= 1
                continue
            if choice == 'r' and page < total_pages - 1:
                page += 1
                continue
            if choice == 'z':
                return None
            
            # 验证选择是否在当前页
            valid_keys = [k for k, _ in page_items] # 当前页有效键列表
            if choice in valid_keys:
                name, unlocked, cost = options[choice]
                
                if not unlocked:
                    say(f"对方摇了摇头：'阁下功力尚浅，尚未领悟此招（需{cost}能量）。'")
                    continue  # 保持在当前页
                
                if self.game.attribute.energy_get(True) < cost:
                    say(f"能量不足{cost}点，无法施展此招！")
                    continue  # 保持在当前页
                
                return choice  # 返回选项键
            
            # 无效输入
            say("该招式未习得，你思虑再三决定重新出招。")
            # 继续循环，保持在当前页

    def _build_skill_menu(      # 构建技能菜单选项
            self, category: str, level: str) -> Dict[str, Tuple[str, bool, int]]: 
        options: Dict[str, Tuple[str, bool, int]] = {}
        key_index = ord('a')  # 初始值 = 97 98→'b'

        # 遍历技能缓存，筛选出对应类别的技能
        for skill_data in self.game._skill_cache.values():
            
            if skill_data.category != category or skill_data.level != level:
                continue

            # 检查能量是否足够解锁该技能
            current_energy = self.game.attribute.energy_get(True)
            unlocked = current_energy >= skill_data.cost
            
            # 构建 options
            options[chr(key_index)] = (skill_data.name, unlocked, skill_data.cost)
            key_index += 1
        options['z'] = (None, True, 0)  # 返回上级选项
        return options
 
    def _get_available_levels(  # 获取指定类别的level
            self, category: str) -> List[str]:    
        levels = set()  # 集合
        for skill_data in self.game._skill_cache.values():
            if skill_data.category == category:
                levels.add(skill_data.level)
        levels = sorted(levels) # 转化为有序列表
        return levels
    
    def debug_state(self):
        """调试状态信息"""
        print(f"\n=== 菜单状态调试 ===")
        print(f"栈深度: {len(self.stack.stack)}")
        for i, state in enumerate(self.stack.stack):
            print(f"  {i}: {state}")
        current = self.get_current_state()
        print(f"当前菜单: {current.menu_type if current else 'None'}")
        print(f"是否根菜单: {self.stack.is_root()}")

    def run(self) -> Any:   # 运行Menu
        if not self.get_current_state():
            self.stack.clear()
            self.stack.push('main')
    
        while True:
            current_state = self.get_current_state()

            # case1：当前没有菜单
            if not current_state:
                self.stack.clear()
                self.stack.push('main')
                current_state = self.get_current_state()
                break
            result = None

            # case2：正常启动菜单
            menu_type = current_state.menu_type
            result = None

            if menu_type == 'main':
                result = self.menu_main()
            elif menu_type == 'category':
                result = self.menu_category()
            elif menu_type == 'level':
                result = self.menu_level()

            # case3：特殊结果
            if isinstance(result, str) and "对方显然很有侠客精神" in result:
                say(result)
                continue
            elif isinstance(result, str) and "对方仰天一笑" in result:
                return 'escape'
            if result is not None:
                return result
    
    def menu_main(self)-> Optional[str]:        # 主菜单
        current_state = self.get_current_state()
        if current_state.menu_type != 'main':
            return None
        while 1:
            print("\n【回合开始】你略加思索,决定:")
            print("  [a] 攻击")
            print("  [b] 防御")
            print("  [h] 帮助")
            if self.stack.is_root():
                print("  [q] 逃跑") # 栈底
            else:
                print("  [z] 返回上级")
            choice = input(">>> ").strip().lower()

            if choice == 'a':
                self.navigate_to('category', {'category': 'attack'})
                return None
            elif choice == 'b':
                self.navigate_to('category', {'category': 'defense'})
                return None
            elif choice == 'h':
                # 帮助菜单实现
                say("对方显然很有侠客精神，叮嘱你拳可剑、剑可刀、刀可枪、枪可拳，随着招式的熟练可以释放更具威力的招式。")
                return None
            elif choice == 'z' and not self.stack.is_root():
                self.go_back()
                return None
            elif choice == 'q' and self.stack.is_root():
                return 'exit'  # 返回退出标识
            else:
                say("无效的选择，请重新输入。")

    def menu_category(self) -> Optional[str]:   # 行动类别菜单，一级子菜单
        current_category = self.get_current_state() # 获取当前类别
        if current_category.menu_type != 'category': # 防御检测
            return NameError
        
        category = current_category.context.get('category','')
        levels = self._get_available_levels(category)
        if not levels:  # 防御检测
            print(f"当前没有可用的{category}技能")
            self.go_back() 
            return None
        
        options = {}
        key_index = ord('a') # 97+
        for level in levels:
            # 统计该等级下的技能数量
            skill_count = sum(1 for skill in self.game._skill_cache.values() 
                            if skill.category == category and skill.level == level)
            options[chr(key_index)] = (f"{level}级技能 ({skill_count}种)", True, 0)
            key_index += 1
        options['z'] = ("返回上级", True, 0)

        # 显示菜单,并分页
        choice = self._render_menu(options, f"选择{category}技能等级", current_category.page,False)
    
        if choice is None:  # 防御检测
            print("没有此菜单")
            self.go_back()
            return None

        # 更新状态
        self._update_state_selection(choice,options)

        if choice == 'z':
            self.go_back()
            return None
            # 进入等级菜单

        if choice in options and choice != 'z':
            level_index = ord(choice) - ord('a')
            if level_index < len(levels):
                selected_level = levels[level_index]
                self.navigate_to('level', {
                    'category': category,
                    'level': selected_level
                })

        return None
    
    def menu_level(self) -> Optional[str]:      # 等级菜单，二级子菜单
        current_level = self.get_current_state() # 获取当前类别
        if current_level.menu_type != 'level': # 防御检测
            return NameError
        category = current_level.context.get('category', '')
        level = current_level.context.get('level', '')
        options = self._build_skill_menu(category, level)
        skill_options = {k: v for k, v in options.items() if k != 'z'}
        if not skill_options:   # 防御检测
            print(f"在{category}的{level}等级中没有可用技能")
            self.go_back()
            return None
        
        choice = self._render_menu(options, f"选择{category}技能 - {level}", current_level.page)

        # 处理技能选择
        if choice in options and choice != 'z':
            # 获取选中的技能名
            skill_name, unlocked, cost = options[choice]
            
            # 验证解锁状态和能量
            if not unlocked:
                say(f"技能'{skill_name}'尚未解锁，需要{cost}能量")
                return None
                
            if self.attribute.energy_get(True) < cost:
                say(f"能量不足{cost}点，无法施展{skill_name}！")
                return None
            
            # 获取完整的技能数据
            try:
                skill_data = self.game.get_skill(skill_name)
            except KeyError:
                say(f"技能'{skill_name}'数据异常")
                return None
            
            # 选择成功，返回主菜单并返回选择结果
            self.stack.clear()
            self.stack.push('main')
            
            return skill_name
        return None

