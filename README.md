<div align="center">

```
 __  __  ___ _      _    _   _  ____
|  \/  |/ __| |    / \  | \ | |/ ___|
| |\/| | |  | |   / _ \ |  \| | |  _
| |  | | |__| |__/ ___ \| |\  | |_| |
|_|  |_|\____|_____/   \_\_| \_|\____|
```

# McLang

**用麦当劳菜单写代码的编程语言。**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![零依赖](https://img.shields.io/badge/dependencies-0-4C1?style=flat-square)](https://github.com/lucklyme/mclang)
[![图灵完备](https://img.shields.io/badge/Turing-complete-FFC72C?style=flat-square&logo=duckduckgo&logoColor=black)](https://en.wikipedia.org/wiki/Turing_completeness)
[![MCP](https://img.shields.io/badge/MCP-麦当劳官方-FFC72C?style=flat-square)](https://github.com/M-China/mcd-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**你的 `Hello, World!` 让你胖了 119 个巨无霸。**

</div>

---

## 这是什么

McLang 是一门 esoteric programming language（深奥编程语言）。
它只有 8 条指令，每一条都是麦当劳菜单上一道**真实在售**的餐品。

```python
麦乐鸡 麦乐鸡 麦乐鸡 香芋派     # +1 +1 +1，然后出餐
```

它是**图灵完备**的——8 条指令恰好一对一覆盖 Brainfuck 的 `+ - > < . , [ ]`，
所以理论上你能用麦当劳菜单写出任何程序。

而且它跑完会给你一张**小票**：你的程序到底"吃"掉了多少卡路里。

---

## 先看结果

下面这段是**真跑出来的**，一个字没改（完整记录在 [实测记录.txt](实测记录.txt)）：

```
$ python -m mclang run examples/hello.mclang --bill

  输出：'Hello, World!\n'
  可读：Hello, World!

  步数：591

                    M c L a n g   消 费 小 票                   
                   （本小票由麦当劳 MCP 真实营养数据计算）                 
  ==============================================================
  品项                 次数           热量       蛋白质
  --------------------------------------------------------------
  巨无霸                43     22059.0k   1161.0g
  麦香鱼                36     11700.0k    576.0g
  麦乐鸡               229      9755.4k    549.6g
  苹果片               219      7008.0k      0.0g
  迷你薯条               43      4558.0k     86.0g
  香芋派                14      3248.0k     28.0g
  板烧鸡腿堡               7      2737.0k    161.0g
  --------------------------------------------------------------
  合计                591     61065.4k   2561.6g
  ==============================================================
  脂肪 2594.6 g    碳水 6433.4 g    钙 16278 mg
  钠   92803 mg  ≈ 食盐 235.7 g
  ==============================================================
  ≈ 119.04 个巨无霸（按热量折算）
  ≈ 每日推荐摄入（2000 kcal）的 3053.3%
  要消耗掉，需跑步 982.39 km（按 60 kg 体重）
  ==============================================================

  营养数据源：SNAPSHOT · data/nutrition.json（MCP 真实抓取）
```

**一个 13 字符的 Hello World，代价是 119 个巨无霸和 982 公里。**
这不是编出来的数字——每一个都乘自麦当劳 MCP 接口返回的真实营养数据。

---

## 30 秒跑起来

**不需要 Token，不需要 `pip install`，什么都不需要。**

```bash
git clone https://github.com/lucklyme/mclang.git
cd mclang
python demo.py
```

就这一条。Python 3.8+，纯标准库，零第三方依赖。

---

## 指令集

| 餐品 | 等价 | 语义 | 为什么是它 |
|:---|:---:|:---|:---|
| `麦乐鸡` | `+` | 当前餐盘 +1 | 往盘子里再放一块麦乐鸡，数量就 +1 |
| `苹果片` | `-` | 当前餐盘 -1 | 拿一块麦乐鸡换成苹果片，健康的负一 |
| `巨无霸` | `>` | 指针右移一格 | 巨无霸分量足，向右一步到位 |
| `迷你薯条` | `<` | 指针左移一格 | 迷你薯条份量小，往回挪一小步 |
| `香芋派` | `.` | 输出当前格的值 | 出餐窗口：把这一格端给客人 |
| `圆筒冰淇淋` | `,` | 读入一个字节 | 接单窗口：客人点什么就接什么 |
| `板烧鸡腿堡` | `[` | 循环开始 | 套餐开始：只要这格还有货，就再来一份 |
| `麦香鱼` | `]` | 循环结束 | 套餐收尾：配一条麦香鱼，回到开头判断 |

英文别名也能用：`nugget` `apple` `bigmac` `fries` `pie` `cone` `grilled` `fish`。
Brainfuck 符号直接喂进来也认。

---

## 它能干什么

### 跑程序

```bash
python -m mclang run examples/hello.mclang                  # Hello, World!
python -m mclang run examples/add.mclang                    # 3 + 4 = 7
python -m mclang run examples/cat.mclang --stdin "麦麦"      # 回音壁
python -m mclang run examples/cn.mclang                     # 中文输出（UTF-8）
```

### 把一句话编译成 McLang

```bash
python -m mclang emit "我想吃麦乐鸡"
```

会生成一段能打印出这句话的 McLang 源码。字多的时候会用乘法循环压缩长度。

### 和 Brainfuck 互转

```bash
python -m mclang to-bf examples/hello.mclang     # McLang  -> Brainfuck
python -m mclang from-bf hello.bf                # Brainfuck -> McLang
```

双向转换是无损的——这也是"图灵完备"这句话的依据，不是嘴上说说。

### 出小票

```bash
python -m mclang run examples/hello.mclang --bill
python -m mclang run examples/hello.mclang --bill --live   # 营养数据实时走 MCP
```

---

## 手写一个程序看看

`examples/add.mclang` 是手写的，演示循环怎么用：

```
麦乐鸡 麦乐鸡 麦乐鸡          # 第 1 格 = 3
巨无霸                       # 走到第 2 格
麦乐鸡 麦乐鸡 麦乐鸡 麦乐鸡    # 第 2 格 = 4

板烧鸡腿堡                   # 套餐开始：只要第 2 格还有货
  迷你薯条                   #   回到第 1 格
  麦乐鸡                     #   加一块麦乐鸡
  巨无霸                     #   走到第 2 格
  苹果片                     #   拿掉一块（健康抵扣）
麦香鱼                       # 套餐结束
...
香芋派                       # 出餐
```

跑出来是 `7`。

---

## 为什么这事儿成立

**1. 它真能跑，不是 PPT。** 29 项单元测试，包含循环乘法、字节回绕、UTF-8 输出、
死循环保护、括号配对，以及"生成的代码跑完必须还原原文"这类往返测试。

**2. 数字是真的。** 8 条指令对应的 8 道餐品，营养数据全部来自麦当劳官方 MCP
的 `list-nutrition-foods` 接口（160 个真实在售餐品）。小票上每个数字都能追到源。

**3. 图灵完备有依据。** 8 条指令双射到 Brainfuck 的 8 个符号，互转无损。

**4. 点子落在"没用但好玩"上。** 世界上不缺好用的工具，缺的是让人想转发的东西。

---

## 数据从哪来

```
MCP Server:  https://mcp.mcd.cn        （麦当劳中国官方）
用到的工具:   list-nutrition-foods      （160 个餐品的能量/蛋白质/脂肪/碳水/钠/钙）
```

- **离线模式（默认）**：`data/nutrition.json` 是真实接口返回值的快照，所以不配 Token 也能跑。
- **实时模式**：设好环境变量就能直连官方接口。

```bash
export MCD_MCP_TOKEN=你的Token      # Windows: set MCD_MCP_TOKEN=你的Token
python demo.py --live
```

两种模式算出来的数字是一致的（有测试兜底）。详见 [MCP_INTEGRATION.md](MCP_INTEGRATION.md)。

> ⚠️ Token 只走环境变量，仓库里只有 `${MCD_MCP_TOKEN}` 占位符，不会也不能提交真实凭证。

---

## 项目结构

```
mclang/
├── mclang/
│   ├── isa.py         指令集 + 真实营养数据加载
│   ├── vm.py          词法/语法/虚拟机（Brainfuck 等价）
│   ├── emit.py        代码生成器 + Brainfuck 互转
│   ├── bill.py        小票生成（热量/钠/运动量换算）
│   ├── mcp_live.py    实时拉取 MCP 数据（零依赖 urllib）
│   └── cli.py         命令行
├── examples/          hello / add / cat / cn / mclang
├── data/              nutrition.json（MCP 真实快照）
├── tests/             29 项单元测试
├── demo.py            一键演示
└── 实测记录.txt        真实执行输出，原样保存
```

跑测试：

```bash
python -m unittest discover -s tests
```

---

## 实测记录

以下命令在 Windows / Python 3.13 下逐条执行，输出**原样照抄**，未做任何修饰。
完整版本见 [实测记录.txt](实测记录.txt)。

**① 3 + 4 = 7**（手写程序，演示循环）

```
$ python -m mclang run examples/add.mclang

  输出：'7'
  可读：7
  步数：112
```

**② 回音壁**（读什么吐什么）

```
$ python -m mclang run examples/cat.mclang --stdin 麦麦

  输出：'麦麦'
  可读：麦麦
  步数：20
```

**③ 中文输出**（按 UTF-8 字节流跑，汉字没问题）

```
$ python -m mclang run examples/cn.mclang

  输出：'你好，麦麦\n'
  可读：你好，麦麦

  步数：1305
```

**④ 把一句话编译成 McLang**

```
$ python -m mclang emit 麦
巨无霸麦乐鸡麦乐鸡麦乐鸡板烧鸡腿堡迷你薯条苹果片苹果片苹果片苹果片苹果片苹果片苹果片巨无霸苹果片麦香鱼迷你薯条苹果片苹果片香芋派巨无霸麦乐鸡麦乐鸡麦乐鸡麦乐鸡麦乐鸡板烧鸡腿堡迷你薯条苹果片苹果片苹果片苹果片苹果片苹果片苹果片苹果片苹果片巨无霸苹果片麦香鱼迷你薯条苹果片苹果片香芋派巨无霸麦乐鸡麦乐鸡麦乐鸡麦乐鸡板烧鸡腿堡迷你薯条苹果片苹果片苹果片苹果片苹果片巨无霸苹果片麦香鱼迷你薯条香芋派
```

「麦」的 UTF-8 是 3 个字节，所以你会看到三组结构相同的片段——每组都在凑一个字节，
最后用 `香芋派` 出餐。眼尖的话能发现里面嵌了乘法循环（板烧鸡腿堡…麦香鱼），
那是为了少写几个 `苹果片`。

**⑤ 把 Brainfuck 翻译成 McLang**

```
$ echo '++[->+++<]>.' > t.bf && python -m mclang from-bf t.bf
麦乐鸡麦乐鸡板烧鸡腿堡苹果片巨无霸麦乐鸡麦乐鸡麦乐鸡迷你薯条麦香鱼巨无霸香芋派
```

**⑥ 测试**

```
$ python -m unittest discover -s tests
----------------------------------------------------------------------
Ran 29 tests in 0.014s

OK
```

---

## 关于

为「麦当劳程序员创意开发大赛」而写，基于麦当劳官方 MCP Server 构建。

语言设计上致敬了 esolang 传统里的 [Chef](https://esolangs.org/wiki/Chef)（用菜谱编程）
和 [Piet](https://esolangs.org/wiki/Piet)（用图像编程）——既然菜谱能编程，菜单当然也行。

MIT 协议。餐品名称与营养数据版权归金拱门（中国）有限公司所有，本项目仅作技术演示。

<div align="center">

**现在就去跑一下，看看你的代码值几个巨无霸。**

</div>
