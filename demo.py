#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
McLang 一键演示 —— 零 Token、零依赖，clone 下来直接跑：

    python demo.py                # 用内置真实快照
    python demo.py --live         # 营养数据实时从麦当劳 MCP 拉取
    python demo.py --text "Hi"    # 把你自己的话编译成 McLang

McLang：一门用麦当劳菜单当指令的编程语言。图灵完备，且跑完会给你一张小票。
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mclang import (  # noqa: E402
    VM,
    build_bill,
    emit_text,
    from_bf,
    instruction_table,
    load_nutrition,
    nutrition_from_mcp,
    parse,
    pretty,
    render_bill,
    to_bf,
)

BANNER = r"""
  __  __  ___ _      _    _   _  ____
 |  \/  |/ __| |    / \  | \ | |/ ___|
 | |\/| | |  | |   / _ \ |  \| | |  _
 | |  | | |__| |__/ ___ \| |\  | |_| |
 |_|  |_|\____|_____/   \_\_| \_|\____|
          麦当劳菜单编程语言  ·  esoteric / turing-complete
"""

ROOT = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = os.path.join(ROOT, "examples")


def _load(name: str) -> str:
    with open(os.path.join(EXAMPLES, name), "r", encoding="utf-8") as f:
        return f.read()


def _nutrition(live: bool):
    if live:
        try:
            from mclang import mcp_live

            rows = mcp_live.fetch_nutrition()
            if rows:
                got = nutrition_from_mcp(rows)
                if got:
                    return got, f"LIVE · mcp.mcd.cn（实时拉取 {len(rows)} 个真实餐品）"
        except Exception as exc:  # 网络不通就退回快照，demo 永远能跑
            print(f"  [提示] 实时拉取失败（{exc}），改用内置快照\n")
    return load_nutrition(), "SNAPSHOT · data/nutrition.json（MCP 真实抓取）"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="McLang 一键演示")
    ap.add_argument("--live", action="store_true", help="营养数据实时走 MCP")
    ap.add_argument("--text", default=None, help="把这句话编译成 McLang 并运行")
    ap.add_argument("--weight", type=float, default=60.0, help="体重(kg)，算跑步距离")
    args = ap.parse_args(argv)

    print(BANNER)
    print("  零第三方依赖 · 纯标准库 · Python 3.8+\n")

    nutrition, source = _nutrition(args.live)

    # 1. 指令集
    print("  " + "=" * 78)
    print("  1. 指令集：8 条，每条指令是一道真实在售的麦当劳餐品".center(74))
    print("  " + "=" * 78)
    print(instruction_table())
    print("  8 条指令恰好覆盖 Brainfuck 的 + - > < . , [ ]，故 McLang 图灵完备。\n")

    # 2. 跑 Hello World
    print("  " + "=" * 78)
    print("  2. 跑一个 Hello, World!".center(74))
    print("  " + "=" * 78)
    hello = _load("hello.mclang")
    prog = parse(hello)
    res = VM().run(prog)
    print(f"\n  源码（前 120 个字）：{pretty(hello, per_line=40).splitlines()[0][:120]}...")
    print(f"  指令条数：{len(prog.tokens)}")
    print(f"  等价 Brainfuck：{to_bf(hello)[:70]}...")
    print(f"\n  >>> 输出：{res.output!r}")
    print(f"  >>> 可读：{res.output.strip()}")

    # 3. 小票
    print("\n  " + "=" * 78)
    print("  3. 小票：这段程序吃掉了一份什么订单".center(74))
    print("  " + "=" * 78)
    bill = build_bill(res.counts, nutrition, res.steps)
    print(render_bill(bill, weight_kg=args.weight))
    print(f"  营养数据源：{source}\n")

    # 4. 编译器
    print("  " + "=" * 78)
    print("  4. 编译器：把任意一句话编译成 McLang".center(74))
    print("  " + "=" * 78)
    text = args.text or "McLang"
    src = emit_text(text)
    got = VM().run(parse(src)).output
    print(f"\n  输入：{text!r}")
    print(f"  编译得到 {len(parse(src).tokens)} 条指令，例如：")
    print("    " + pretty(src, per_line=6).splitlines()[0])
    print(f"  运行它，输出：{got!r}   {'✓ 一致' if got == text else '✗ 不一致'}")

    # 5. 与 Brainfuck 互转
    print("\n  " + "=" * 78)
    print("  5. 与 Brainfuck 互转（等价性证明）".center(74))
    print("  " + "=" * 78)
    bf = "++[->+++<]>."
    print(f"\n  Brainfuck : {bf}")
    print(f"  -> McLang : {from_bf(bf)}")
    print(f"  -> 再转回 : {to_bf(from_bf(bf))}   "
          f"{'✓ 一致' if to_bf(from_bf(bf)) == bf else '✗ 不一致'}")

    print("\n  " + "=" * 78)
    print("  试试这些：".center(74))
    print("  " + "=" * 78)
    print("""
    python -m mclang isa                                 查看指令集
    python -m mclang run examples/add.mclang             3 + 4 = 7
    python -m mclang run examples/cat.mclang --stdin 麦麦  回音壁
    python -m mclang emit "你想说的话"                     编译成 McLang
    python -m mclang run examples/hello.mclang --bill     跑完出小票
    python demo.py --live                                营养数据实时走 MCP
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
