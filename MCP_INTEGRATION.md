# MCP 集成说明

## 一、接入的 MCP Server

| 项目 | 值 |
|---|---|
| 服务地址 | `https://mcp.mcd.cn` |
| 提供方 | 麦当劳（中国）有限公司 · 官方 MCP Server |
| 传输协议 | Streamable HTTP（JSON-RPC 2.0） |
| 认证方式 | Header `Authorization: Bearer <Token>` |
| 限流 | 600 次 / 分钟（超出返回 429） |
| Token 申请 | https://open.mcd.cn/mcp → 登录 → 控制台 → 激活 |

## 二、调用了哪些 Tool

本项目调用了 **`list-nutrition-foods`**。

它返回麦当劳 160 个真实在售餐品的营养成分，字段包括：
`productName` / `energyKj` / `energyKcal` / `protein` / `fat` / `carbohydrate` / `sodium` / `calcium`。

**这是整个项目的数据基石。** McLang 的 8 条指令各对应一道真实餐品，
小票上的每一个数字（热量、蛋白质、钠、运动量）都由这条接口的返回值计算得出。

### 指令与真实餐品的对应关系

| 指令 | MCP 返回的餐品名 | 热量(kcal) | 蛋白质(g) | 备注 |
|:---|:---|---:|---:|:---|
| `麦乐鸡` | 麦乐鸡5块 | 213 | 12 | 按「一块」计，故单块 42.6 kcal |
| `苹果片` | 苹果片 | 32 | 0 | |
| `巨无霸` | 巨无霸 | 513 | 27 | 小票按它折算"几个巨无霸" |
| `迷你薯条` | 迷你薯条 | 106 | 2 | |
| `香芋派` | 香芋派 | 232 | 2 | |
| `圆筒冰淇淋` | 圆筒冰淇淋 | 93 | 2 | |
| `板烧鸡腿堡` | 板烧鸡腿堡 | 391 | 23 | |
| `麦香鱼` | 麦香鱼 | 325 | 16 | |

以上数值取自 2026-10-15 的接口真实返回，未经人工修改。

## 三、接口返回格式与解析

`list-nutrition-foods` 的 `data` 字段返回的是一段**自定义表格文本**，而非 JSON 数组，形如：

```
[160]{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:
  猪柳麦满分,null,1288,308,16,16,24,781,213
  麦乐鸡5块,null,890,213,12,12,13,422,9
  ...
```

`mclang/mcp_live.py` 中的 `parse_nutrition_text()` 负责解析：

1. 用正则从 `{...}` 中提取字段名列表
2. 逐行按逗号切分并映射到字段
3. 数值字段转 `float`，`null` 归一为空字符串
4. 跳过表头行与空行

同一餐品在列表里可能有多个规格（如「麦乐鸡5块」与「麦乐鸡4块」）。
**只取首次匹配项**，保证实时模式与离线快照的计算口径完全一致（有测试覆盖）。

## 四、离线 / 实时双模式

| 模式 | 触发方式 | 数据源 | 是否需要 Token |
|:---|:---|:---|:---|
| 离线（默认） | `python demo.py` | `data/nutrition.json` | ❌ 不需要 |
| 实时 | `python demo.py --live` | 直连 `mcp.mcd.cn` | ✅ 需要 |

`data/nutrition.json` 是接口真实返回值的快照，因此**不配置 Token 也能完整体验**，
两条路径算出的结果一致（见 `tests/test_mclang.py`）。

## 五、调用示例

```bash
curl -s -X POST https://mcp.mcd.cn \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${MCD_MCP_TOKEN}" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list-nutrition-foods","arguments":{}}}'
```

## 六、凭证安全

- Token **只从环境变量 `MCD_MCP_TOKEN` 读取**，代码中无任何硬编码。
- 仓库内的配置文件模板 `mcp-config.example.json` 仅含 `${MCD_MCP_TOKEN}` 占位符。
- 项目发布前已做全量扫描，确认无真实 Token 泄露。
- 未配置 Token 时，程序会给出明确的获取指引并自动回退到离线快照，不会报错中断。

## 七、错误处理

| 情况 | 处理 |
|:---|:---|
| 401 未授权 | 提示 Token 无效或过期 |
| 429 限流 | 提示单 Token 每分钟 600 次上限 |
| 网络异常 | `demo.py` 自动回退离线快照并提示；CLI 下直接抛出可读错误 |
| 数据格式变化 | 解析失败时给出明确报错，不会静默产出错误数字 |
