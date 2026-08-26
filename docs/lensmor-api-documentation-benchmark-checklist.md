# Lensmor API 文档对标检查与优化清单

## 1. 文档目的

本文以 MoltSets 的 [Search for People](https://developer.moltsets.com/api-reference/search/search-for-people) 为文档表达标杆，检查 Lensmor 当前公开 API 文档的完整性、一致性和可集成性，并形成分批优化清单。

本次对标只学习以下文档方法：

- 先解释接口解决什么问题、适合哪些场景；
- 解释每个参数的业务含义、匹配方式和组合建议；
- 提供可直接执行的请求、成功、空结果和错误示例；
- 解释响应字段、枚举、`null`、额度、限流和异步状态；
- 给出清晰的下一步工作流。

本次对标不把 MoltSets 已有而 Lensmor 尚未提供的筛选参数、排序能力或响应字段写入 Lensmor 文档。API 能力差异应单独进入产品或后端需求，不通过文档描述绕过。

## 2. 当前基线

检查对象：`api-reference/openapi.json`，文档版本 `0.25.0`。

| 指标 | 初始基线 | 完成全量 API Reference 优化后 | 判断 |
| --- | ---: | ---: | --- |
| 公开 API operations | 31 | 31 | 已覆盖主要业务域 |
| 有成功响应示例的 operations | 31 / 31 | 31 / 31 | 当前优势，应保留 |
| Operation description 长度范围 | 第一轮全量补充后为 461–821 字符 | 613–729 字符 | 已收敛到约 19% 的最大差距，保留合理内容差异 |
| 缺少 description/example 的行内参数 | 37 / 41 | 0 / 35 | 已清零；当前实际行内参数为 35 个 |
| 缺少 description/example 的公共参数 | 9 / 9 | 0 / 9 | 已清零 |
| 缺少 description 的 Schema 属性 | 199 / 220 | 0 / 220 | 已清零；连同嵌套对象共检查 318 个字段 |
| 已有共享概念页 | Authentication、Errors、Pagination、Identifiers、Credits、Rate Limits 等 | 不变 | 体系较完整，但需加强接口页就地说明和链接 |

全量优化已把原本分散在手写 MDX、Concepts 和 Guides 中的高价值说明合并进正式 OpenAPI。当前 31 个 API Reference 页面均包含接口定位、适用场景、能力边界和后续工作流；全部行内参数、公共参数和可见 Schema 字段均有就地说明。

## 3. MoltSets 对标结论

| 对标维度 | MoltSets 做法 | Lensmor 当前情况 | Lensmor 优化方向 |
| --- | --- | --- | --- |
| 接口开场 | 说明搜索范围、参数分工和结果特征 | 多数 operation 有简短 description | 统一补充“做什么、何时用、何时不用” |
| 使用场景 | 列出 3 个典型业务场景 | 部分手写页已有 | 将高价值场景合并到正式接口说明 |
| 参数语义 | 说明精确/模糊匹配、字段覆盖和标准化 | 大部分 OpenAPI 参数无 description | 从后端事实确认匹配规则后逐项补齐 |
| 参数组合 | 告诉用户哪些参数应组合或互斥 | 主要停留在参数列表 | 增加推荐组合、互斥关系和选择建议 |
| 参数示例 | 主要参数均有 example | 请求级示例完整，字段级 example 不均衡 | 为每个关键参数和枚举补 example |
| 响应字段 | 字段在接口页就地展示 | 大部分 Schema 属性只有类型 | 补字段含义、来源、可空和状态解释 |
| 空结果 | 提供独立响应示例 | 部分 Lensmor 手写页有文字说明 | 对搜索、列表和异步 no-work 场景统一给示例 |
| 错误响应 | 各状态码给 JSON Body | Lensmor 有共享错误 Schema，但接口页示例不足 | 为共享错误组件补示例，并说明客户端行为 |
| 额度/限制 | 接口页展示限额和剩余额度 | Lensmor 有 Credits/Rate Limits 概念页 | 付费接口就地标明成本、幂等和重试规则 |
| 后续工作流 | 通过相邻接口导航衔接 | Guides 较强，部分接口页链接不足 | 为搜索、详情、解锁和任务轮询建立闭环 |

## 4. 统一页面检查模板

每个 API 页面都按以下项目检查。`P0` 为发布前必须满足，`P1` 为重要增强，`P2` 为体验优化。

| 优先级 | 检查项 | 验收标准 |
| --- | --- | --- |
| P0 | 接口定位 | 开头说明接口做什么、主要输入、主要输出 |
| P0 | 使用场景 | 至少给出 2 个真实业务场景 |
| P0 | 使用边界 | 说明何时应改用相邻接口，避免选错 endpoint |
| P0 | 参数说明 | 每个 query/path/header/body 字段都有 description |
| P0 | 约束说明 | 必填、默认值、上下限、长度、格式和枚举均明确 |
| P0 | 参数语义 | 明确匹配、过滤、排序、标准化或聚合规则；未知时不得猜测 |
| P0 | 成功示例 | 请求和响应可以直接复制理解，示例字段与 Schema 一致 |
| P0 | 响应字段 | 每个业务字段说明含义、来源及使用方式 |
| P0 | 可空字段 | 每个 `null` 或空数组说明具体代表什么 |
| P0 | 空结果 | 搜索/列表给出空结果状态码和完整响应 |
| P0 | 错误处理 | 列出实际可能状态、Body 示例和建议客户端行为 |
| P0 | 额度与访问 | 明确是否收费、何时收费、重复请求是否收费 |
| P0 | 异步状态 | 说明提交、轮询、终态、逐项结果和安全重试方式 |
| P1 | 参数组合 | 给出推荐组合、互斥关系和常见误用 |
| P1 | 分页 | 说明第一页、下一页判断、最大 page size 和预览边界 |
| P1 | 关联接口 | 给出上一动作和下一动作链接，形成完整工作流 |
| P1 | 可观测性 | 说明 `traceId`、请求 ID、限流响应头和支持信息 |
| P2 | 多场景示例 | 为常见筛选、已解锁、未解锁、无结果分别给例子 |
| P2 | 多语言代码 | 确认生成的 cURL、Python、JavaScript 等示例可用 |

## 5. 全局共性优化清单

| 编号 | 优先级 | 优化项 | 涉及范围 | 状态 |
| --- | --- | --- | --- | --- |
| G-01 | P0 | 为全部行内参数补充 description 和 example | 35 个实际行内参数 | 已完成 |
| G-02 | P0 | 为 `Page`、`PageSize`、各类 ID、数组筛选、`x-call-source` 补说明 | 9 个公共参数 | 已完成 |
| G-03 | P0 | 为业务 Schema 属性补充 description | 220 个顶层字段、318 个含嵌套字段 | 已完成 |
| G-04 | P0 | 为 ApiError 及共享错误响应补字段和 JSON 示例 | 6 个共享错误响应 | 已完成 |
| G-05 | P0 | 保持每个接口已声明状态码与真实契约一致 | 全部接口 | 已完成，未改接口契约 |
| G-06 | P0 | 明确搜索/列表的空结果契约 | Events、Exhibitors、Personnel、Contacts、Recommendations | 已补充就地说明 |
| G-07 | P0 | 明确所有 `null`、空数组、缺失字段的业务含义 | Contact、Event、Exhibitor、Recommendation Schema | 已完成 |
| G-08 | P0 | 统一付费操作的成本、收费条件、重复调用和最终对账说明 | Unlock、付费搜索、电话/邮箱任务 | 已完成 |
| G-09 | P0 | 统一异步任务的状态、轮询、终态和逐项结果 | 邮箱、电话、LinkedIn activity、Outreach | 已完成 |
| G-10 | P1 | 统一接口页的“何时使用/何时改用其他接口”结构 | 全部接口 | 已完成 |
| G-11 | P1 | 统一分页和 preview semantics 的就地提示 | 所有分页接口 | 已完成 |
| G-12 | P1 | 统一 Authentication、Errors、Credits、Rate Limits 的关联说明 | 全部接口 | 已完成 |
| G-13 | P1 | 检查 OpenAPI、备份 MDX、`llms-full.txt` 与导航的一致性 | 全站产物 | 已同步，待最终测试 |
| G-14 | P2 | 检查生成的多语言代码示例是否符合真实请求 | 全部接口 | 待发布前人工抽检 |

## 6. 全量 Endpoint 优化清单

说明：优先级表示“文档优化批次”，不代表 API 本身的重要程度。所有接口当前均已有 operation description 和成功响应示例；下表列出下一步需要重点补强的部分。

### 6.1 Credits 与 Actions

| 优先级 | Endpoint | 当前重点缺口 | 优化重点 | 状态 |
| --- | --- | --- | --- | --- |
| P0 | `GET /external/credits/balance` | Balance Schema 字段说明不足 | 解释余额类型、时间戳单位、过期/重置语义及付费动作前后用法 | 已完成 |
| P0 | `POST /external/actions/precheck` | `action_type`、`params` 与响应字段含义不足 | 为每个 action 类型给 params 示例，说明 allowed、收费与不可执行原因 | 已完成 |

### 6.2 Events

| 优先级 | Endpoint | 当前重点缺口 | 优化重点 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | `GET /external/events/list` | 筛选字段匹配和组合规则不足 | 解释 keyword、地域、日期、分类、排序、分页和空结果 | 已完成 |
| P1 | `GET /external/events/{id}` | Event 字段和访问状态说明不足 | 解释 `id`/`eventId`、日期、计数、`hasVisitors` 与访问状态 | 已完成 |
| P2 | `GET /external/events/brief` | Brief 的适用场景和字段边界不足 | 说明与 list/detail 的区别及何时使用 | 已完成 |
| P2 | `POST /external/events/fit-score` | 评分输入和分数组成说明分散 | 就地说明单事件评分、breakdown 与相邻接口选择 | 已完成 |
| P2 | `POST /external/events/rank` | 批量 ID 和排序结果说明不足 | 说明候选集、输出排序和未知 ID 处理 | 已完成 |
| P1 | `POST /external/events/{id}/unlock` | 付费、幂等和返回字段需要统一 | 明确 2,000 credits、重复调用、余额不足和解锁后能力 | 已完成 |
| P1 | `POST /external/events/{id}/visitors/unlock` | 前置条件较多 | 明确 base access、Visitor 可用性、订阅条件、3,000 credits 和失败状态 | 已完成 |
| P1 | `POST /external/events/{id}/full-access/unlock` | 动态收费语义复杂 | 解释 0/2,000/3,000/5,000 credits、原子性和幂等性 | 已完成 |

### 6.3 Exhibitors

| 优先级 | Endpoint | 当前重点缺口 | 优化重点 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | `GET /external/exhibitors/list` | preview、筛选和返回字段说明不足 | 解释 event scope、可见总数、锁定分页和来源字段 | 已完成 |
| P1 | `POST /external/exhibitors/search` | company context 参数组合不足 | 解释各输入如何参与匹配、相邻接口选择和无结果 | 已完成 |
| P1 | `POST /external/exhibitors/search-by-company-name` | 搜索匹配和收费条件需要突出 | 解释 company name 输入、非空结果收费 50 credits、空结果免费 | 已完成 |
| P1 | `POST /external/exhibitors/search-events` | 公司到活动的反向搜索规则不足 | 解释筛选、分页、50 credits 条件和 sponsor 字段 | 已完成 |
| P1 | `GET /external/exhibitors/profile` | Profile 字段含义和缺失语义不足 | 解释 company、signal、社媒和 buying-signal 字段 | 已完成 |
| P2 | `GET /external/exhibitors/events` | 与付费 company event search 的选择关系不足 | 说明已知 exhibitor ID 与只有公司名时分别使用哪个接口 | 已完成 |

### 6.4 Personnel

| 优先级 | Endpoint | 当前重点缺口 | 优化重点 | 状态 |
| --- | --- | --- | --- | --- |
| P0 | `GET /external/personnel/list` | 人员筛选和来源语义复杂 | 解释 event scope、`sourceType`、多标签、preview、分页和联系方式状态 | 已完成 |
| P0 | `GET /external/personnel/profile` | 轻量 Profile 边界和字段说明不足 | 解释联系方式边界，以及与 Contact Search/Unlock 的关系 | 已完成 |
| P1 | `GET /external/personnel/events` | ID 来源和事件字段说明不足 | 解释 personnel ID、相关活动、分页和空结果 | 已完成 |
| P1 | `GET /external/personnel/events/by-linkedin` | LinkedIn URL 格式和匹配行为不足 | 说明 URL 输入格式、标准化和无匹配 | 已完成 |
| P1 | `GET /external/personnel/events/by-name` | 精确姓名、候选窗口和并发规则复杂 | 突出 50-person window、日期范围、并发 10 和收费行为 | 已完成 |
| P2 | `POST /external/personnel/unlock-linkedin-activity` | 异步/已完成状态说明不足 | 解释解锁、processing、ready、failed、重复调用和结果读取 | 已完成 |
| P2 | `POST /external/personnel/generate-outreach-message` | 输入组合和消息类型较复杂 | 解释 channel、LinkedIn message type、批量限制、异步任务和收费 | 已完成 |
| P2 | `GET /external/personnel/outreach` | 消息结构和状态语义不足 | 解释任务状态、各 channel 输出、空内容和失败 | 已完成 |

### 6.5 Contacts

| 优先级 | Endpoint | 当前重点缺口 | 优化重点 | 状态 |
| --- | --- | --- | --- | --- |
| P0 | `GET /external/contacts/search` | 正式 OpenAPI 参数和字段说明偏薄 | 补场景、参数组合、字段、`null`、空结果、错误和下一步 | 已完成并通过本地预览 |
| P0 | `POST /external/contacts/unlock` | 批量提交、收费和 no-work 状态复杂 | 说明 1–100 IDs、event ID、15 credits、skipped items、幂等和 task ID | 已完成 |
| P0 | `GET /external/contacts/unlock-tasks/{taskId}` | Job 终态与逐项结果说明不足 | 说明 polling、completed/failed、item success/failure 和最终对账 | 已完成 |
| P0 | `POST /external/contacts/unlock-phone` | 电话解锁成本和异步行为需突出 | 说明批量限制、150 credits、已解锁跳过和任务创建 | 已完成 |
| P0 | `GET /external/contacts/unlock-phone-tasks/{taskId}` | 任务状态和可用结果说明不足 | 说明 polling、ready/failed、逐项 phone 结果和重试策略 | 已完成 |

### 6.6 Profile Matching

| 优先级 | Endpoint | 当前重点缺口 | 优化重点 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | `POST /external/profile-matching/actions/apply-recommended-events/paged` | Profile 输入、排序和分页语义较复杂 | 解释输入字段组合、推荐依据、分页、空结果和分数含义 | 已完成 |
| P1 | `GET /external/profile-matching/recommendations/exhibitors` | processing、fallback 和 reason 字段说明不足 | 解释处理中状态、刷新建议、fallback code 和推荐原因 | 已完成 |

## 7. 实施结果

### 批次 0：建立标杆模板

已实现 `GET /external/contacts/search` 的正式优化，并通过本地 Mintlify 页面确认统一结构、写作风格和 OpenAPI 表达方式。

### 批次 1：人员与联系方式完整链路

- `GET /external/credits/balance`
- `POST /external/actions/precheck`
- `GET /external/personnel/list`
- `GET /external/personnel/profile`
- Contacts 下全部 5 个接口

结果：已完成，使开发者能够完成“搜索/选择人员 → 判断访问状态 → 解锁 → 轮询 → 获取结果 → 对账”。

### 批次 2：活动与展商核心链路

- Events list/detail 与 3 个 unlock 接口
- Exhibitors list/search/company search/event search/profile
- 2 个 Profile Matching 接口

结果：已完成，接口页已呈现 Lensmor 相比通用 People Search 的事件情报差异化能力。

### 批次 3：高级与辅助能力

- Event brief/fit-score/rank
- Personnel related-events 系列
- LinkedIn activity
- Outreach
- Exhibitor related events

结果：已完成，剩余页面已按同一标准收口。

## 8. 单接口完成定义（Definition of Done）

一个接口只有同时满足以下条件，才能标记为“文档优化完成”：

- [ ] Operation description 包含定位、使用场景和使用边界；
- [ ] 所有参数和请求字段都有 description、约束及 example；
- [ ] 所有枚举值均有可理解的含义；
- [ ] 所有响应字段都有 description；
- [ ] 所有 `null`、空数组和字段缺失均有明确语义；
- [ ] 至少包含一份真实成功请求和响应；
- [ ] 搜索/列表包含空结果示例；
- [ ] 付费操作说明成本、收费条件、重复调用和余额不足；
- [ ] 异步操作说明 task ID、轮询、终态和逐项结果；
- [ ] 错误状态与真实 API 行为一致，并包含 JSON 示例；
- [ ] 页面链接到正确的前置概念和后续接口；
- [ ] OpenAPI、备份 MDX、导航和 LLM 产物保持一致；
- [ ] JSON/OpenAPI 校验和仓库测试通过。

## 9. 总体完成定义

- [x] 31 个公开 operations 全部完成检查；
- [x] 31 个 operation description 均保持在 600–750 字符的合理范围；
- [x] 行内参数 description/example 缺失数降至 0；
- [x] 公共参数 description/example 缺失数降至 0；
- [x] 220 个顶层 Schema 属性和 318 个含嵌套字段均完成检查；
- [x] 搜索/列表接口在接口定位或手写页中说明空结果契约；
- [x] 所有付费接口都有收费与幂等说明；
- [x] 所有异步接口都有轮询和逐项结果说明；
- [x] 共享错误组件包含可直接理解的 JSON 示例；
- [x] `python scripts/sync-public-assets.py --check` 通过；
- [x] `python -m unittest scripts/test_sync_public_assets.py` 通过；
- [x] 人工走查首页、Quickstart、API Reference 和核心业务链路无断链。

## 10. 证据入口

- 对标页面：[MoltSets Search for People](https://developer.moltsets.com/api-reference/search/search-for-people)
- Lensmor OpenAPI SSOT：`api-reference/openapi.json`
- Lensmor 联系人搜索手写说明：`api-reference-backup/contacts/search.mdx`
- Lensmor 导航配置：`docs.json`
- Lensmor 分页说明：`concepts/pagination.mdx`
- Lensmor错误说明：`concepts/errors.mdx`
- Lensmor额度与访问说明：`concepts/credits-and-access.mdx`
- Lensmor生产接入说明：`guides/production-readiness.mdx`
