"""McLang 指令集架构（Instruction Set Architecture）。

McLang 是一门 esoteric programming language（深奥编程语言）：
指令不是符号，而是麦当劳菜单上的真实餐品。

它在计算能力上等价于 Brainfuck —— 8 条指令、一条无限长的纸带、
一个指针、一格一个字节。因此 McLang 是图灵完备的。

隐喻：
    纸带   = 一条无限长的取餐传送带
    格子   = 传送带上的餐盘（每格装 0-255）
    指针   = 你现在站的位置
    +1     = 往餐盘里放一块麦乐鸡
    -1     = 拿走一块（用苹果片"健康抵扣"）
    输出   = 出餐
    输入   = 接单
    循环   = 一份套餐（吃完一份再来一份，直到条件不满足）
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Brainfuck 等价符号 —— 用于互转与证明等价性
BF_INC = "+"
BF_DEC = "-"
BF_RIGHT = ">"
BF_LEFT = "<"
BF_OUT = "."
BF_IN = ","
BF_LOOP_OPEN = "["
BF_LOOP_CLOSE = "]"


@dataclass(frozen=True)
class Instruction:
    """一条 McLang 指令。"""

    food: str  # 中文餐品名（主写法）
    bf: str  # 等价 Brainfuck 符号
    meaning: str  # 语义
    joke: str  # 为什么是它
    aliases: tuple = field(default_factory=tuple)  # 其它可接受的写法

    @property
    def all_names(self) -> List[str]:
        return [self.food, *self.aliases]


# ---------------------------------------------------------------------------
# 指令表：顺序即文档顺序
# ---------------------------------------------------------------------------

INSTRUCTIONS: List[Instruction] = [
    Instruction(
        food="麦乐鸡",
        bf=BF_INC,
        meaning="当前餐盘 +1",
        joke="往盘子里再放一块麦乐鸡，数量就 +1",
        aliases=("nugget", "McNugget", "麦乐鸡块"),
    ),
    Instruction(
        food="苹果片",
        bf=BF_DEC,
        meaning="当前餐盘 -1",
        joke="拿一块麦乐鸡换成苹果片，健康的负一",
        aliases=("apple", "AppleSlice"),
    ),
    Instruction(
        food="巨无霸",
        bf=BF_RIGHT,
        meaning="指针右移一格",
        joke="巨无霸分量足，向右一步到位",
        aliases=("bigmac", "BigMac"),
    ),
    Instruction(
        food="迷你薯条",
        bf=BF_LEFT,
        meaning="指针左移一格",
        joke="迷你薯条份量小，往回挪一小步",
        aliases=("fries", "MiniFries", "小薯条"),
    ),
    Instruction(
        food="香芋派",
        bf=BF_OUT,
        meaning="输出当前餐盘的值（出餐）",
        joke="出餐窗口：把这一格端给客人",
        aliases=("pie", "TaroPie", "派"),
    ),
    Instruction(
        food="圆筒冰淇淋",
        bf=BF_IN,
        meaning="读入一个字节到当前餐盘（接单）",
        joke="接单窗口：客人点什么，就接什么",
        aliases=("cone", "Cone", "冰淇淋"),
    ),
    Instruction(
        food="板烧鸡腿堡",
        bf=BF_LOOP_OPEN,
        meaning="循环开始（套餐开始）",
        joke="套餐开始：只要这格还有货，就再来一份",
        aliases=("grilled", "GrilledChicken", "板烧"),
    ),
    Instruction(
        food="麦香鱼",
        bf=BF_LOOP_CLOSE,
        meaning="循环结束（套餐结束）",
        joke="套餐收尾：配一条麦香鱼，回到开头判断",
        aliases=("fish", "FiletOFish", "麦香魚"),
    ),
]

# 任意写法 -> Instruction
_BY_NAME: Dict[str, Instruction] = {}
for _ins in INSTRUCTIONS:
    for _name in _ins.all_names:
        _BY_NAME[_name] = _ins
    # Brainfuck 符号本身也接受，方便直接跑 BF 程序
    _BY_NAME[_ins.bf] = _ins

FOOD_TO_BF: Dict[str, str] = {i.food: i.bf for i in INSTRUCTIONS}
BF_TO_FOOD: Dict[str, str] = {i.bf: i.food for i in INSTRUCTIONS}


def lookup(token: str) -> Optional[Instruction]:
    """按任意写法查指令；查不到返回 None。"""
    return _BY_NAME.get(token)


def is_instruction(token: str) -> bool:
    return token in _BY_NAME


# ---------------------------------------------------------------------------
# 营养数据（来自麦当劳 MCP 真实接口）
# ---------------------------------------------------------------------------

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "nutrition.json",
)


@dataclass
class Nutrition:
    food: str
    mcp_name: str
    energy_kcal: float
    protein_g: float
    fat_g: float
    carbohydrate_g: float
    sodium_mg: float
    calcium_mg: float
    pieces_per_serving: int = 1

    @property
    def kcal_per_unit(self) -> float:
        """单个指令单位的热量。

        「麦乐鸡」一次是 +1 块，而 MCP 返回的是「麦乐鸡5块」的热量，
        因此要除以份数，保证「+1 = 一块」。
        """
        return self.energy_kcal / max(1, self.pieces_per_serving)


def load_nutrition(path: str = DATA_PATH) -> Dict[str, Nutrition]:
    """加载真实营养数据（离线快照）。"""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    out: Dict[str, Nutrition] = {}
    for food, d in raw.get("foods", {}).items():
        out[food] = Nutrition(
            food=food,
            mcp_name=d.get("mcp_name", food),
            energy_kcal=float(d.get("energy_kcal", 0)),
            protein_g=float(d.get("protein_g", 0)),
            fat_g=float(d.get("fat_g", 0)),
            carbohydrate_g=float(d.get("carbohydrate_g", 0)),
            sodium_mg=float(d.get("sodium_mg", 0)),
            calcium_mg=float(d.get("calcium_mg", 0)),
            pieces_per_serving=int(d.get("pieces_per_serving", 1)),
        )
    return out


def nutrition_from_mcp(foods: List[Dict[str, Any]]) -> Dict[str, Nutrition]:
    """把 MCP 返回的餐品列表折算成指令营养表。

    只保留指令集用到的餐品，其余忽略。
    """
    out: Dict[str, Nutrition] = {}
    wanted = {i.food: True for i in INSTRUCTIONS}
    by_mcp_name = {i.food: i for i in INSTRUCTIONS}
    for d in foods or []:
        name = str(d.get("productName", "")).strip()
        # MCP 返回的是「麦乐鸡5块」这类带份数的名字，需要归一到指令名
        matched = None
        for food in wanted:
            if name == food or name.startswith(food):
                matched = food
                break
        if matched is None:
            continue
        # 同一餐品在列表里可能有多个规格（如「麦乐鸡5块」「麦乐鸡4块」）。
        # 只认第一次匹配到的，避免被后面的规格覆盖，保证与离线快照口径一致。
        if matched in out:
            continue
        pieces = 1
        ins = by_mcp_name[matched]
        out[matched] = Nutrition(
            food=matched,
            mcp_name=name or ins.food,
            energy_kcal=float(d.get("energyKcal", 0) or 0),
            protein_g=float(d.get("protein", 0) or 0),
            fat_g=float(d.get("fat", 0) or 0),
            carbohydrate_g=float(d.get("carbohydrate", 0) or 0),
            sodium_mg=float(d.get("sodium", 0) or 0),
            calcium_mg=float(d.get("calcium", 0) or 0),
            pieces_per_serving=5 if matched == "麦乐鸡" else 1,
        )
    return out


def instruction_table() -> str:
    """渲染指令集表格（README / CLI 共用）。"""
    lines = [
        f"  {'餐品':<12} {'BF':>3}  {'语义':<26} 为什么是它",
        "  " + "-" * 92,
    ]
    for i in INSTRUCTIONS:
        lines.append(
            f"  {i.food:<12} {i.bf:>3}  {i.meaning:<26} {i.joke}"
        )
    lines.append("  " + "-" * 92)
    return "\n".join(lines)
