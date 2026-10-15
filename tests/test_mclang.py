"""McLang 测试套件。"""

from __future__ import annotations

import os
import unittest

from mclang import (
    VM,
    build_bill,
    emit_text,
    from_bf,
    instruction_table,
    load_nutrition,
    parse,
    pretty,
    to_bf,
    tokenize,
)
from mclang.isa import BF_TO_FOOD, FOOD_TO_BF, INSTRUCTIONS
from mclang.vm import McLangError, StepLimitExceeded

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXAMPLES = os.path.join(ROOT, "examples")


def run_source(src: str, stdin_data: str = "") -> str:
    return VM().run(parse(src), stdin_data=stdin_data).output


def load_example(name: str) -> str:
    with open(os.path.join(EXAMPLES, name), "r", encoding="utf-8") as f:
        return f.read()


class TestISA(unittest.TestCase):
    def test_eight_instructions(self):
        self.assertEqual(len(INSTRUCTIONS), 8)

    def test_bf_symbols_complete(self):
        """8 条指令必须正好覆盖 Brainfuck 的全部 8 个符号 —— 这是图灵完备的依据。"""
        self.assertEqual(
            set(FOOD_TO_BF.values()), set("+-><.,[]")
        )
        self.assertEqual(len(set(FOOD_TO_BF.values())), 8)
        self.assertEqual(set(BF_TO_FOOD.keys()), set("+-><.,[]"))

    def test_food_bf_is_bijective(self):
        self.assertEqual(len(FOOD_TO_BF), len(BF_TO_FOOD))
        for food, bf in FOOD_TO_BF.items():
            self.assertEqual(BF_TO_FOOD[bf], food)

    def test_table_renders(self):
        text = instruction_table()
        for ins in INSTRUCTIONS:
            self.assertIn(ins.food, text)


class TestLexer(unittest.TestCase):
    def test_greedy_chinese_match(self):
        """「香芋派」不能被切成别的。"""
        toks = tokenize("香芋派")
        self.assertEqual(len(toks), 1)
        self.assertEqual(toks[0].food, "香芋派")

    def test_alias_alias(self):
        toks = tokenize("nugget nugget pie")
        self.assertEqual([t.food for t in toks], ["麦乐鸡", "麦乐鸡", "香芋派"])

    def test_bf_symbols_accepted(self):
        """Brainfuck 源码可以直接喂进来。"""
        toks = tokenize("++>.")
        self.assertEqual([t.bf for t in toks], ["+", "+", ">", "."])

    def test_comments_and_whitespace_ignored(self):
        toks = tokenize("# 这是注释\n麦乐鸡  # 也是注释\n麦乐鸡")
        self.assertEqual([t.food for t in toks], ["麦乐鸡", "麦乐鸡"])

    def test_unbalanced_open(self):
        with self.assertRaises(McLangError):
            parse("板烧鸡腿堡 麦乐鸡")

    def test_unbalanced_close(self):
        with self.assertRaises(McLangError):
            parse("麦香鱼")


class TestVM(unittest.TestCase):
    def test_inc_and_output(self):
        out = VM().run(parse("麦乐鸡 麦乐鸡")).output
        self.assertEqual(out, "")

    def test_hello_example(self):
        self.assertEqual(run_source(load_example("hello.mclang")), "Hello, World!\n")

    def test_cn_example_utf8(self):
        self.assertEqual(run_source(load_example("cn.mclang")), "你好，麦麦\n")

    def test_add_example(self):
        """手写的 3+4，应输出字符 '7'。"""
        self.assertEqual(run_source(load_example("add.mclang")), "7")

    def test_cat_example(self):
        self.assertEqual(
            run_source(load_example("cat.mclang"), stdin_data="麦麦"), "麦麦"
        )

    def test_loop_multiplication(self):
        """++[->+++<] ：第 1 格的 2 被消耗掉，第 2 格累加成 6。"""
        src = from_bf("++[->+++<]")
        prog = parse(src)
        res = VM().run(prog)
        self.assertEqual(res.tape_snapshot[0], 0)  # 被循环吃光
        self.assertEqual(res.tape_snapshot[1], 6)  # 2 次 × 3 = 6
        self.assertEqual(res.ptr, 0)

    def test_cell_wraps_at_256(self):
        src = from_bf("-")  # 0 - 1 -> 255
        res = VM().run(parse(src))
        self.assertEqual(res.tape_snapshot[0], 255)

    def test_ptr_left_underflow_raises(self):
        with self.assertRaises(McLangError):
            VM().run(parse("迷你薯条"))

    def test_step_limit_protects(self):
        vm = VM(step_limit=1000)
        with self.assertRaises(StepLimitExceeded):
            vm.run(parse(from_bf("+[]")))


class TestEmit(unittest.TestCase):
    def test_emit_roundtrip_ascii(self):
        for text in ("Hi", "Hello, World!", "McLang"):
            self.assertEqual(run_source(emit_text(text)), text)

    def test_emit_roundtrip_unicode(self):
        for text in ("你好", "麦当劳", "🍔"):
            self.assertEqual(run_source(emit_text(text)), text)

    def test_bf_roundtrip(self):
        bf = "++[->+++<]>." 
        self.assertEqual(to_bf(from_bf(bf)), bf)

    def test_mclang_to_bf_matches(self):
        src = "麦乐鸡 麦乐鸡 香芋派"
        self.assertEqual(to_bf(src), "++.")

    def test_pretty_keeps_semantics(self):
        src = emit_text("Hi")
        self.assertEqual(run_source(pretty(src, per_line=4)), "Hi")


class TestBill(unittest.TestCase):
    def setUp(self):
        self.nutrition = load_nutrition()

    def test_nugget_kcal_per_piece(self):
        """MCP 返回的是「麦乐鸡5块」，+1 是一块，必须除以 5。"""
        n = self.nutrition["麦乐鸡"]
        self.assertEqual(n.energy_kcal, 213)
        self.assertEqual(n.pieces_per_serving, 5)
        self.assertAlmostEqual(n.kcal_per_unit, 42.6, places=4)

    def test_all_instructions_have_real_nutrition(self):
        for ins in INSTRUCTIONS:
            self.assertIn(ins.food, self.nutrition, f"{ins.food} 缺少真实营养数据")

    def test_bill_totals_match_items(self):
        prog = parse(load_example("hello.mclang"))
        res = VM().run(prog)
        bill = build_bill(res.counts, self.nutrition, res.steps)
        s = sum(i.kcal for i in bill.items)
        self.assertAlmostEqual(bill.total_kcal, s, places=6)
        self.assertGreater(bill.total_kcal, 0)

    def test_bill_counts_match_steps(self):
        prog = parse(load_example("hello.mclang"))
        res = VM().run(prog)
        bill = build_bill(res.counts, self.nutrition, res.steps)
        self.assertEqual(sum(i.count for i in bill.items), res.steps)

    def test_bigmac_equivalence_is_sane(self):
        prog = parse(load_example("hello.mclang"))
        res = VM().run(prog)
        bill = build_bill(res.counts, self.nutrition, res.steps)
        expected = bill.total_kcal / self.nutrition["巨无霸"].kcal_per_unit
        self.assertAlmostEqual(bill.bigmac_equiv, expected, places=6)

    def test_intro_example_prints_A(self):
        """入门例子：65 块麦乐鸡 + 出餐 == 字母 A（ASCII 65）。"""
        res = VM().run(parse(load_example("a.mclang")))
        self.assertEqual(res.output, "A")
        self.assertEqual(res.steps, 66)
        self.assertEqual(res.counts["麦乐鸡"], 65)
        self.assertEqual(res.counts["香芋派"], 1)

    def test_all_examples_parse_and_run(self):
        """examples/ 下的示例都必须能被解析并成功执行。"""
        ex_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
        files = sorted(f for f in os.listdir(ex_dir) if f.endswith(".mclang"))
        self.assertIn("a.mclang", files)
        for name in files:
            prog = parse(load_example(name))
            # cat.mclang 读 stdin，给点输入避免空转
            VM(step_limit=200000).run(prog, stdin_data="麦麦")  # 不抛异常即通过


if __name__ == "__main__":
    unittest.main(verbosity=2)
