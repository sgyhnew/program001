from time import sleep
import json
from typing import Dict, Any, Iterator, Tuple


def say(txt, delay=1, end='\n'):                                    # 模拟说话停顿，增加观感
    print(txt, end=end, flush=True)
    sleep(delay)
def load_json(file_path: str, encoding='utf-8') -> Dict[str, Any]:  # 通用JSON加载函数
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
# def build_effects(data: Dict[str, Any]) -> Dict[str, Any]:           # 递归遍历，为每个effect字符串绑定打印函数
#     for key, value in data.items():
#         if isinstance(value, dict):
#             if "effect" in value and isinstance(value["effect"], str):
#                 # 核心：字符串 → 打印函数
#                 effect_text = value["effect"]
#                 value["effect"] = lambda txt=effect_text: print(txt)
#             else:
#                 build_effects(value)
#     return data

