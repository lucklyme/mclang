"""McLang 命令行入口。

    python -m mclang isa                        查看指令集
    python -m mclang run examples/hello.mclang  跑一个程序
    python -m mclang run examples/hello.mclang --bill   跑完顺便出小票
    python -m mclang emit "Hi"                  把字符串编译成 McLang 源码
    python -m mclang to-bf examples/hello.mclang        转成 Brainfuck
    python -m mclang from-bf hello.bf           把 Brainfuck 翻译成 McLang
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from . import isa
from .bill import build_bill, render_bill
from .emit import emit_text, from_bf, pretty, to_bf
from .vm import VM, McLangError, parse

EXAMPLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples"
)


def _nutrition(live: bool = False):
    """加载营养数据。live 时走 MCP，否则用内置真实快照。"""
    if live:
        from . import mcp_live

        rows = mcp_live.fetch_nutrition()
        if rows:
            got = isa.nutrition_from_mcp(rows)
            if got:
                return got, f"LIVE · mcp.mcd.cn（{len(rows)} 个真实餐品）"
    return isa.load_nutrition(), "SNAPSHOT · data/nutrition.json（MCP 真实抓取）"


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _build() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="mclang",
        description="McLang —— 麦当劳菜单编程语言（图灵完备 / 零依赖）",
    )
    sub = ap.add_subparsers(dest="command")

    sub.add_parser("isa", help="打印指令集")

    p_run = sub.add_parser("run", help="运行一个 .mclang 程序")
    p_run.add_argument("file", help=".mclang 文件路径")
    p_run.add_argument("--bill", action="store_true", help="跑完出一张小票")
    p_run.add_argument("--stdin", default="", help="作为「接单」输入的字符串")
    p_run.add_argument("--live", action="store_true", help="小票数据实时从 MCP 拉取")
    p_run.add_argument("--weight", type=float, default=60.0, help="体重(kg)，算跑步距离用")
    p_run.add_argument("--trace", action="store_true", help="打印纸带快照")

    p_emit = sub.add_parser("emit", help="把字符串编译成 McLang 源码")
    p_emit.add_argument("text")
    p_emit.add_argument("--wrap", type=int, default=0, help="每行多少条指令，0=不换行")

    p_to = sub.add_parser("to-bf", help="McLang -> Brainfuck")
    p_to.add_argument("file")

    p_from = sub.add_parser("from-bf", help="Brainfuck -> McLang")
    p_from.add_argument("file")
    p_from.add_argument("--wrap", type=int, default=0)

    sub.add_parser("examples", help="列出内置示例程序")
    return ap


def main(argv=None) -> int:
    ap = _build()
    args = ap.parse_args(argv)

    if not args.command:
        ap.print_help()
        return 0

    if args.command == "isa":
        print()
        print("  McLang 指令集 · 8 条 · 等价于 Brainfuck，故图灵完备".center(96))
        print()
        print(isa.instruction_table())
        print()
        return 0

    if args.command == "examples":
        print("\n  内置示例：")
        if os.path.isdir(EXAMPLES_DIR):
            for name in sorted(os.listdir(EXAMPLES_DIR)):
                if name.endswith(".mclang"):
                    print(f"    {name}")
        print("\n  运行：python -m mclang run examples/hello.mclang --bill\n")
        return 0

    if args.command == "run":
        src = _read(args.file)
        prog = parse(src)
        vm = VM()
        result = vm.run(prog, stdin_data=args.stdin or "")
        print(f"\n  输出：{result.output!r}")
        if result.output:
            print(f"  可读：{result.output}")
        print(f"  步数：{result.steps}")
        if args.trace:
            print(f"  纸带：{result.tape_snapshot[:16]}  (ptr={result.ptr})")

        if args.bill:
            nutrition, source = _nutrition(live=args.live)
            bill = build_bill(result.counts, nutrition, result.steps)
            print(render_bill(bill, weight_kg=args.weight))
            print(f"  营养数据源：{source}\n")
        else:
            print()
        return 0

    if args.command == "emit":
        src = emit_text(args.text)
        if args.wrap and args.wrap > 0:
            print(pretty(src, per_line=args.wrap))
        else:
            print(src)
        return 0

    if args.command == "to-bf":
        print(to_bf(_read(args.file)))
        return 0

    if args.command == "from-bf":
        src = from_bf(_read(args.file))
        if args.wrap and args.wrap > 0:
            print(pretty(src, per_line=args.wrap))
        else:
            print(src)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
