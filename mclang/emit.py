"""McLang 代码生成与互转。

三件事：
    1. emit_text()   —— 把任意字符串编译成一段能输出它的 McLang 程序
    2. from_bf()     —— 把 Brainfuck 源码翻译成 McLang
    3. to_bf()       —— 把 McLang 翻译回 Brainfuck（用于证明二者等价）
"""

from __future__ import annotations

from typing import List, Tuple

from . import isa
from .vm import parse

F = isa.BF_TO_FOOD  # BF 符号 -> 餐品名


def _repeat(bf: str, n: int) -> str:
    return bf * n


def _best_factor(d: int) -> Tuple[int, int, int]:
    """把 d 拆成 a*b + r，使 a + b + |r| 最小（用于生成更短的循环）。"""
    best = (0, 0, d)
    best_cost = abs(d)
    a = 2
    while a * a <= abs(d) + 64:
        b = d // a
        r = d - a * b
        cost = a + abs(b) + abs(r)
        if cost < best_cost:
            best_cost = cost
            best = (a, b, r)
        a += 1
    return best


def _emit_delta(delta: int) -> str:
    """生成「把当前格子增加 delta」的 Brainfuck 片段（delta 可为负）。"""
    if delta == 0:
        return ""
    # 取绝对值更小的等价表示（利用 256 取模回绕）
    d = delta % 256
    if d > 128:
        d -= 256
    neg = d < 0
    n = abs(d)
    sign = isa.BF_DEC if neg else isa.BF_INC

    # 小数值直接平铺；大数值用乘法循环压缩
    if n <= 12:
        return _repeat(sign, n)

    a, b, r = _best_factor(n)
    if a < 2 or b == 0:
        return _repeat(sign, n)

    loop = (
        isa.BF_RIGHT
        + _repeat(isa.BF_INC, a)
        + isa.BF_LOOP_OPEN
        + isa.BF_LEFT
        + _repeat(sign, b)
        + isa.BF_RIGHT
        + isa.BF_DEC
        + isa.BF_LOOP_CLOSE
        + isa.BF_LEFT
    )
    rem = _repeat(sign, abs(r)) if r else ""
    return loop + rem


def emit_text(text: str) -> str:
    """生成一段 McLang 程序，运行后输出 text。"""
    bf_parts: List[str] = []
    cur = 0
    for ch in text.encode("utf-8"):
        bf_parts.append(_emit_delta(ch - cur))
        bf_parts.append(isa.BF_OUT)
        cur = ch
    return from_bf("".join(bf_parts))


def from_bf(bf_src: str) -> str:
    """Brainfuck -> McLang 源码。非指令字符原样保留。"""
    out: List[str] = []
    for ch in bf_src:
        food = isa.BF_TO_FOOD.get(ch)
        out.append(food if food else ch)
    return "".join(out)


def to_bf(mclang_src: str) -> str:
    """McLang -> Brainfuck 源码。"""
    return parse(mclang_src).to_bf()


def pretty(mclang_src: str, per_line: int = 8) -> str:
    """把一长串指令按固定个数换行，便于阅读。"""
    prog = parse(mclang_src)
    lines: List[str] = []
    for i in range(0, len(prog.tokens), per_line):
        lines.append("".join(t.food for t in prog.tokens[i : i + per_line]))
    return "\n".join(lines)
