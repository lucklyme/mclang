# WorkBuddy 开发上下文

> 本文件记录 McLang 使用腾讯 WorkBuddy 智能体完成的开发过程，
> 用于核验「麦当劳程序员创意开发大赛 × WorkBuddy」联动奖励条件。

## 1. 使用的 WorkBuddy 能力

| 能力 | 在项目中的具体用途 |
|---|---|
| 连接器 · 自定义 MCP | 在 WorkBuddy 中配置并启用 `mcd-mcp`，直连 `https://mcp.mcd.cn`，实时拉取 160 个餐品的真实营养数据 |
| 网页读取 / 信息提取 | 抓取官方活动仓库 README、`activityGuidelines.md`、`RANKING.md`，完成赛制与竞品分析 |
| 本地文件读写与代码生成 | 生成语言设计、虚拟机、代码生成器、小票引擎、测试用例与全部参赛文档 |
| 命令执行 | 运行 `demo.py`、执行单元测试、验证输出正确性、做发布前安全扫描 |

## 2. 通过 WorkBuddy 直连 MCP 的实证记录

WorkBuddy 侧配置（`~/.workbuddy/mcp.json`）：

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": { "Authorization": "Bearer ${MCD_MCP_TOKEN}" }
    }
  }
}
```

以下 MCP 工具均通过 WorkBuddy 实际调用成功（真实响应，非模拟）：

| 调用 | 结果 |
|---|---|
| `tools/list` | HTTP 200，返回 35 个工具（官方 README 仅列出 30 个，文档滞后） |
| `now-time-info` | 返回服务器时间 `2026-10-15 22:09:47 GMT+08:00` |
| `list-nutrition-foods` | **本项目数据源**：返回 160 个真实在售餐品的能量/蛋白质/脂肪/碳水/钠/钙 |
| `query-my-account` | 返回积分账户：可用 0 / 累计 310.5 / 已过期 305.5 |
| `mall-points-products` | 返回积分商城商品（用于同一账号下另一项目 mcd-point-fx） |
| `query-lottery-info` | 返回奖池 10 个奖品，单次消耗 24 积分 |
| `campaign-calendar` / `available-coupons` | 营销日历与可领券（选题阶段的数据勘察） |

## 3. 关键开发对话摘要

1. **赛制分析**：WorkBuddy 读完官方规则后指出排名机制是纯 GitHub Star 排序、无技术评审，
   且同一账号多项目只取 Star 最高者。据此建议：与其摊多个，不如集中资源做单个。
2. **赛道定位**：对 104 个上榜项目按名称归类，发现点餐助手（18+）、省钱比价（14+）、
   MBTI 玄学（11+）已极度拥挤；同时注意到 **McOracle 仅凭一个双关梗就排到第 2（294 star）**，
   据此判断"程序员幽默 × 麦当劳"的传播效率高于正经工具。
3. **方向选择**：用户提出"要有意思、意想不到、可能没用但好玩"，
   WorkBuddy 给出三个候选（菜单编程语言 / 抽卡模拟器 / 猜词游戏）并说明各自取舍，
   用户选定 **McLang**——一门用麦当劳餐品当指令的 esoteric language，并确定为新的主力项目。
4. **语言设计**：8 条指令一一对应麦当劳真实在售餐品，且恰好双射到 Brainfuck 的
   `+ - > < . , [ ]`，从而**可论证地图灵完备**；隐喻上把纸带比作取餐传送带、
   把 `+1` 比作往餐盘里放一块麦乐鸡、把循环比作「一份套餐」。
5. **点题功能**：提出"程序跑完出小票"——把每条指令的执行次数乘以该餐品的真实营养数据，
   得出这份程序消耗了多少卡路里、相当于几个巨无霸、要跑几公里。
   实测 `Hello, World!` = **119.04 个巨无霸 / 982.39 公里**，这个数字成为项目的传播点。
6. **缺陷发现与修复**：
   - 手写示例 `add.mclang` 首版输出 `0` 而非 `7`，根因是循环结束后指针停在第 2 格，
     后续代码却按"停在第 1 格"书写。修正后输出正确，并保留注释说明指针位置。
   - 实时模式与离线快照的总热量不一致（59096 vs 61065），根因是 `nutrition_from_mcp`
     被列表里靠后的「麦乐鸡4块」覆盖了靠前的「麦乐鸡5块」。改为**只取首次匹配**后两者完全一致。
   - 单元测试 `test_loop_multiplication` 首版断言写错（误以为结果在第 1 格），
     实为解释器正确、测试错误，已修正为断言第 1 格归零、第 2 格为 6。
7. **发布**：WorkBuddy 建立 Public 仓库、推送代码、配置 topics，并提交报名 Issue。

## 4. 产出清单

- 语言核心：`mclang/`（`isa.py` 指令集与营养数据、`vm.py` 虚拟机、`emit.py` 代码生成与 BF 互转、
  `bill.py` 小票引擎、`mcp_live.py` 实时接入、`cli.py` 命令行）
- 示例程序：`examples/`（hello / add / cat / cn / mclang）
- 真实数据快照：`data/nutrition.json`（MCP 真实返回）
- 单元测试：`tests/test_mclang.py`（31 项，全部通过）
- 一键演示：`demo.py`（零第三方依赖、零 Token 可跑）
- 参赛文档：`README.md` / `CONTEST_DECLARATION.md` / `MCP_INTEGRATION.md` / `mcp-config.example.json` / 本文件

## 5. 合规说明

- 本文件不含任何真实 Token、密钥或账号凭证。
- 项目中所有涉及凭证的位置均使用 `${MCD_MCP_TOKEN}` 环境变量占位符。
- 未读取、未存储任何第三方个人信息；所用数据均为麦当劳官方 MCP 的公开餐品营养数据。
- 餐品名称与营养数据版权归金拱门（中国）有限公司所有，本项目仅作技术演示。
