"""小票生成器 —— McLang 的点题功能。

一段 McLang 程序跑完之后，它其实「吃掉」了一份订单：
每条指令执行了多少次，就等于你往传送带上放了多少份对应的餐品。

把这些乘上麦当劳 MCP 返回的真实营养数据，就得到一张小票：
这段代码跑完，你摄入了多少大卡、相当于几个巨无霸、要跑几公里才消耗得掉。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from . import isa
from .isa import Nutrition

# 参考常量
DAILY_KCAL = 2000.0  # 成人每日推荐摄入（通用参考值）
KCAL_PER_KM_PER_KG = 1.036  # 跑步每公里每公斤体重大致消耗（kcal）
DEFAULT_WEIGHT_KG = 60.0
SODIUM_TO_SALT = 2.54  # 钠(mg) -> 食盐(mg) 换算系数


@dataclass
class LineItem:
    food: str
    count: int
    kcal: float
    protein_g: float
    fat_g: float
    carb_g: float
    sodium_mg: float
    calcium_mg: float


@dataclass
class Bill:
    items: List[LineItem]
    total_steps: int
    total_kcal: float
    total_protein_g: float
    total_fat_g: float
    total_carb_g: float
    total_sodium_mg: float
    total_calcium_mg: float

    @property
    def bigmac_equiv(self) -> float:
        """相当于几个巨无霸（按热量）。"""
        bigmac = self._ref_kcal("巨无霸", 513.0)
        return self.total_kcal / bigmac if bigmac else 0.0

    @property
    def daily_pct(self) -> float:
        return self.total_kcal / DAILY_KCAL * 100

    def run_km(self, weight_kg: float = DEFAULT_WEIGHT_KG) -> float:
        """要跑多少公里才能消耗掉。"""
        per_km = KCAL_PER_KM_PER_KG * weight_kg
        return self.total_kcal / per_km if per_km else 0.0

    @property
    def salt_g(self) -> float:
        return self.total_sodium_mg * SODIUM_TO_SALT / 1000.0

    @staticmethod
    def _ref_kcal(food: str, fallback: float) -> float:
        return fallback


def build_bill(
    counts: Dict[str, int],
    nutrition: Dict[str, Nutrition],
    total_steps: int,
) -> Bill:
    """根据「指令执行次数」和真实营养数据生成小票。"""
    items: List[LineItem] = []
    tot = dict(kcal=0.0, p=0.0, f=0.0, c=0.0, na=0.0, ca=0.0)

    for ins in isa.INSTRUCTIONS:
        cnt = int(counts.get(ins.food, 0))
        if cnt <= 0:
            continue
        nut = nutrition.get(ins.food)
        if nut is None:
            continue
        unit = nut.kcal_per_unit
        # 单条指令的营养量按「一份」计，热量按最小单位（如一块麦乐鸡）计
        scale = cnt
        protein = nut.protein_g / max(1, nut.pieces_per_serving) * scale
        fat = nut.fat_g / max(1, nut.pieces_per_serving) * scale
        carb = nut.carbohydrate_g / max(1, nut.pieces_per_serving) * scale
        sodium = nut.sodium_mg / max(1, nut.pieces_per_serving) * scale
        calcium = nut.calcium_mg / max(1, nut.pieces_per_serving) * scale

        items.append(
            LineItem(
                food=ins.food,
                count=cnt,
                kcal=unit * scale,
                protein_g=protein,
                fat_g=fat,
                carb_g=carb,
                sodium_mg=sodium,
                calcium_mg=calcium,
            )
        )
        tot["kcal"] += unit * scale
        tot["p"] += protein
        tot["f"] += fat
        tot["c"] += carb
        tot["na"] += sodium
        tot["ca"] += calcium

    items.sort(key=lambda x: -x.kcal)
    return Bill(
        items=items,
        total_steps=total_steps,
        total_kcal=tot["kcal"],
        total_protein_g=tot["p"],
        total_fat_g=tot["f"],
        total_carb_g=tot["c"],
        total_sodium_mg=tot["na"],
        total_calcium_mg=tot["ca"],
    )


def render_bill(bill: Bill, weight_kg: float = DEFAULT_WEIGHT_KG, width: int = 62) -> str:
    """渲染成一张 ASCII 小票。"""
    L: List[str] = []
    bar = "=" * width
    L.append("")
    L.append("  " + "M c L a n g   消 费 小 票".center(width - 4))
    L.append("  " + "（本小票由麦当劳 MCP 真实营养数据计算）".center(width - 6))
    L.append("  " + bar)
    L.append(f"  {'品项':<12} {'次数':>8} {'热量':>12} {'蛋白质':>9}")
    L.append("  " + "-" * width)

    for it in bill.items:
        L.append(
            f"  {it.food:<12} {it.count:>8} {it.kcal:>11.1f}k {it.protein_g:>8.1f}g"
        )

    L.append("  " + "-" * width)
    L.append(f"  {'合计':<12} {bill.total_steps:>8} {bill.total_kcal:>11.1f}k "
             f"{bill.total_protein_g:>8.1f}g")
    L.append("  " + bar)
    L.append(f"  脂肪 {bill.total_fat_g:.1f} g    碳水 {bill.total_carb_g:.1f} g    "
             f"钙 {bill.total_calcium_mg:.0f} mg")
    L.append(f"  钠   {bill.total_sodium_mg:.0f} mg  ≈ 食盐 {bill.salt_g:.1f} g")
    L.append("  " + bar)
    L.append(f"  ≈ {bill.bigmac_equiv:.2f} 个巨无霸（按热量折算）")
    L.append(f"  ≈ 每日推荐摄入（{DAILY_KCAL:.0f} kcal）的 {bill.daily_pct:.1f}%")
    L.append(f"  要消耗掉，需跑步 {bill.run_km(weight_kg):.2f} km（按 {weight_kg:.0f} kg 体重）")
    L.append("  " + bar)
    L.append("")
    return "\n".join(L)
