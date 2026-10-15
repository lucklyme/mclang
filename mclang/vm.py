"""McLang 虚拟机。

语义与 Brainfuck 一一对应，因此 McLang 是图灵完备的：
    > < + - . , [ ]

除执行结果外，VM 还会统计每条指令的实际执行次数 —— 这是「小票」的数据来源：
程序跑完，你吃掉了一份由指令构成的订单。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import isa


class McLangError(Exception):
    """McLang 的通用错误。"""


class SyntaxError_(McLangError):
    pass


class StepLimitExceeded(McLangError):
    pass


@dataclass
class Token:
    name: str  # 源码中的原始写法
    food: str  # 归一后的餐品名
    bf: str
    pos: int  # 源码字符偏移，用于报错


@dataclass
class Program:
    tokens: List[Token]
    jumps: Dict[int, int] = field(default_factory=dict)  # 循环起止配对

    def to_bf(self) -> str:
        return "".join(t.bf for t in self.tokens)

    def to_source(self, sep: str = "") -> str:
        return sep.join(t.food for t in self.tokens)


# ---------------------------------------------------------------------------
# 词法 + 语法
# ---------------------------------------------------------------------------

def _max_name_len() -> int:
    return max(len(n) for n in isa._BY_NAME.keys())


def tokenize(src: str, strict: bool = False) -> List[Token]:
    """把源码切成指令序列。

    - 中文指令按「最长匹配」扫描（避免「香芋派」被切成别的）
    - 英文别名按连续字母切分
    - '#' 或 '//' 到行尾为注释
    - 其它字符一律忽略（与 Brainfuck 一致）
    """
    tokens: List[Token] = []
    i = 0
    n = len(src)
    max_len = _max_name_len()
    unknown: List[str] = []

    while i < n:
        ch = src[i]

        # 注释
        if ch == "#" or src.startswith("//", i):
            nl = src.find("\n", i)
            i = n if nl == -1 else nl + 1
            continue

        # 空白
        if ch.isspace():
            i += 1
            continue

        # 英文别名：吃掉一整段字母
        if ch.isascii() and ch.isalpha():
            j = i
            while j < n and src[j].isascii() and src[j].isalpha():
                j += 1
            word = src[i:j]
            ins = isa.lookup(word)
            if ins:
                tokens.append(Token(word, ins.food, ins.bf, i))
            elif strict:
                raise SyntaxError_(f"位置 {i}：未知指令 {word!r}")
            else:
                unknown.append(word)
            i = j
            continue

        # 中文 / 符号：最长匹配
        hit = None
        for length in range(min(max_len, n - i), 0, -1):
            cand = src[i : i + length]
            ins = isa.lookup(cand)
            if ins:
                hit = (cand, ins, length)
                break
        if hit:
            cand, ins, length = hit
            tokens.append(Token(cand, ins.food, ins.bf, i))
            i += length
            continue

        if strict:
            raise SyntaxError_(f"位置 {i}：无法识别的字符 {ch!r}")
        i += 1

    return tokens


def parse(src: str, strict: bool = False) -> Program:
    """切词并做括号配对。"""
    tokens = tokenize(src, strict=strict)
    jumps: Dict[int, int] = {}
    stack: List[int] = []
    for idx, t in enumerate(tokens):
        if t.bf == isa.BF_LOOP_OPEN:
            stack.append(idx)
        elif t.bf == isa.BF_LOOP_CLOSE:
            if not stack:
                raise SyntaxError_(
                    f"位置 {t.pos}：「{t.name}」找不到配对的「{isa.BF_TO_FOOD[isa.BF_LOOP_OPEN]}」"
                )
            open_idx = stack.pop()
            jumps[open_idx] = idx
            jumps[idx] = open_idx
    if stack:
        idx = stack[-1]
        t = tokens[idx]
        raise SyntaxError_(
            f"位置 {t.pos}：「{t.name}」没有配套的「{isa.BF_TO_FOOD[isa.BF_LOOP_CLOSE]}」"
        )
    return Program(tokens=tokens, jumps=jumps)


# ---------------------------------------------------------------------------
# 执行
# ---------------------------------------------------------------------------

@dataclass
class RunResult:
    output: str
    steps: int
    counts: Dict[str, int]  # 餐品 -> 执行次数
    tape_snapshot: List[int]
    ptr: int


class VM:
    """McLang 虚拟机。"""

    def __init__(self, tape_size: int = 30000, step_limit: int = 50_000_000):
        self.tape_size = tape_size
        self.step_limit = step_limit

    def run(self, program: Program, stdin_data: str = "") -> RunResult:
        tape = [0] * min(self.tape_size, 1024)  # 惰性增长，先开一小段
        ptr = 0
        pc = 0
        steps = 0
        counts: Dict[str, int] = {i.food: 0 for i in isa.INSTRUCTIONS}
        out_bytes: List[int] = []

        data = stdin_data.encode("utf-8")
        in_pos = 0
        tokens = program.tokens
        jumps = program.jumps
        total = len(tokens)

        while pc < total:
            t = tokens[pc]
            bf = t.bf
            steps += 1
            if steps > self.step_limit:
                raise StepLimitExceeded(
                    f"执行步数超过上限 {self.step_limit}，疑似死循环"
                )

            if bf == isa.BF_INC:
                tape[ptr] = (tape[ptr] + 1) % 256
            elif bf == isa.BF_DEC:
                tape[ptr] = (tape[ptr] - 1) % 256
            elif bf == isa.BF_RIGHT:
                ptr += 1
                if ptr >= len(tape):
                    if len(tape) >= self.tape_size:
                        raise McLangError("指针越界：超出纸带长度")
                    # 惰性扩容
                    tape.extend([0] * max(1024, min(len(tape), self.tape_size - len(tape))))
            elif bf == isa.BF_LEFT:
                ptr -= 1
                if ptr < 0:
                    raise McLangError("指针越界：移到纸带左端之外")
            elif bf == isa.BF_OUT:
                out_bytes.append(tape[ptr])
            elif bf == isa.BF_IN:
                tape[ptr] = data[in_pos] if in_pos < len(data) else 0
                in_pos += 1
            elif bf == isa.BF_LOOP_OPEN:
                if tape[ptr] == 0:
                    pc = jumps[pc]
            elif bf == isa.BF_LOOP_CLOSE:
                if tape[ptr] != 0:
                    pc = jumps[pc]

            counts[t.food] = counts.get(t.food, 0) + 1
            pc += 1

        return RunResult(
            output=bytes(out_bytes).decode("utf-8", errors="replace"),
            steps=steps,
            counts=counts,
            tape_snapshot=tape[: max(8, ptr + 1)],
            ptr=ptr,
        )
