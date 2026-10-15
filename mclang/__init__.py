"""McLang —— 麦当劳菜单编程语言。

一门用麦当劳餐品当指令的 esoteric programming language（深奥编程语言）。
图灵完备（等价于 Brainfuck），零第三方依赖，跑完还会给你一张真实小票。

    from mclang import parse, VM, emit_text, build_bill, load_nutrition

    prog = parse("麦乐鸡 麦乐鸡 香芋派")   # +1 +1 输出
    res = VM().run(prog)
    print(res.output)                       # '\x02'
"""

from .isa import (
    INSTRUCTIONS,
    Instruction,
    Nutrition,
    instruction_table,
    load_nutrition,
    nutrition_from_mcp,
)
from .vm import (
    McLangError,
    Program,
    RunResult,
    StepLimitExceeded,
    VM,
    parse,
    tokenize,
)
from .emit import emit_text, from_bf, pretty, to_bf
from .bill import Bill, LineItem, build_bill, render_bill

__version__ = "1.0.0"
__all__ = [
    "INSTRUCTIONS",
    "Instruction",
    "Nutrition",
    "instruction_table",
    "load_nutrition",
    "nutrition_from_mcp",
    "McLangError",
    "Program",
    "RunResult",
    "StepLimitExceeded",
    "VM",
    "parse",
    "tokenize",
    "emit_text",
    "from_bf",
    "to_bf",
    "pretty",
    "Bill",
    "LineItem",
    "build_bill",
    "render_bill",
]
