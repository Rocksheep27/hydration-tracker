# V3 iPhone Independent PWA Strategy

## 文档状态

V3.1 PWA 方案设计与路线图调整已完成。

V3.2 `pwa/` 纯前端页面骨架已完成：

- 创建 `pwa/index.html`、`pwa/styles.css` 和 `pwa/app.js`。
- 页面包含今日概览、添加记录表单和今日明细空状态。
- 使用内存空状态显示 `0 ml`、默认目标 `2000 ml` 和 `0` 条记录。
- 保存按钮只显示阶段提示，不保存或修改数据。
- 页面可直接在 Mac 浏览器中打开，不需要 Python 服务器。

V3.2 不包含 localStorage、Service Worker、manifest、发布配置、JSON 导入导出、完整项目库或水分计算逻辑。

V3.3 浏览器端项目库和水分计算已完成：

- 21 个常用项目及默认单位、默认重量或容量、基础类型和含水率已迁移到 `pwa/app.js`。
- 页面会按白水、饮品和食物筛选常用项目。
- 选择项目后显示默认单位和换算说明。
- 输入数量后在浏览器端实时估算本次水分，结果最多显示 1 位小数。
- 项目库、纯计算函数和页面渲染函数保持分离。
- 保存按钮仍只显示阶段提示，不写入任何数据。

V3.3 不包含 localStorage、Service Worker、manifest、发布配置或 JSON 导入导出。

V3.4 浏览器本地记录管理已完成：

- 使用稳定 key `hydration_tracker_v3_records` 保存 `{ schema_version, records }`。
- 支持保存、读取和显示今天的记录，并自动更新今日概览。
- 支持二次确认后删除今天的单条记录或清空今天的全部记录。
- 删除与清空都保留其他日期记录，不调用 `localStorage.clear()`。
- 无存储数据时初始化空容器；JSON 损坏或版本不支持时显示错误并停止写入，不覆盖原数据。

V3.4 不包含 Service Worker、manifest、发布配置或 JSON 导入导出。localStorage 不是备份，后续需要提供 JSON 导入导出。

V3.5 iPhone Safari 布局和触控体验优化已完成：

- 页面支持约 `375px` 的窄屏布局，并为 Safari 安全区域保留间距。
- 表单控件、保存按钮和删除按钮具备适合手指操作的触控高度。
- 数量输入使用手机数字键盘提示，备注调整为多行输入。
- 今日明细在窄屏下改为更清晰的上下布局，并保护长名称和备注换行。
- 保存、删除、清空和存储异常提示使用简洁的内联状态样式。
- V3.4 的 localStorage key、数据结构、二次确认和记录管理逻辑保持不变。
- V3.5 基础功能已在真实 iPhone Safari 上手动验证；页面视觉优化后仍建议再次进行真机检查。
- 今日概览增加 CSS `conic-gradient` 进度环，视觉进度最多显示 `100%`，文字保留真实完成率。
- 根据完成率显示六档温和鼓励提示，并随今日数据同步刷新。
- 常用项目和今日明细增加显示用 emoji，不写入 localStorage，也不改变计算逻辑。
- 调整今日明细标题和清空按钮布局，标题在常见 iPhone 宽度下保持单行。
- 优化概览、表单、状态提示、明细和危险操作的视觉层次。
- 修复 iPhone Safari 取消删除或清空确认后危险按钮颜色残留的问题，同时保留键盘焦点提示。
- 保存记录成功后，餐次字段恢复为默认“无餐次”；保存失败时保留用户当前选择。
- 已记录未来扩展常用项目库的字段和旧记录兼容要求。
- 已记录未来自定义食物和饮品记录需求，但尚未实现，建议放在 V4 或 V3.7 之后。

V3.5 不包含 manifest、Service Worker、发布配置或 JSON 导入导出。

V3.6 manifest、图标和基础离线缓存能力已完成：

- 新增 `manifest.json`，声明应用名称、启动地址、显示模式、主题色和图标。
- 新增本地图标资源，供浏览器和主屏幕场景使用。
- 新增基础 Service Worker，只缓存静态资源，不缓存用户记录。
- Service Worker 缓存版本与 localStorage `schema_version` 分开管理。
- 页面会在受支持的浏览器和非 `file://` 场景下尝试注册 Service Worker。
- iPhone Safari 临时测试已通过，可以添加到主屏幕，并以接近独立小工具的方式打开。
- 从主屏幕打开后的记录可保留在对应环境的本地存储中。
- Safari 普通标签页和主屏幕 Web App 的本地数据不应被假定为完全互通。
- `192.168.x.x` 一类局域网地址只适合临时测试，不是最终日常访问方式。
- `file://` 方式仍可预览页面，但不能完整验证 Service Worker。
- 最终完整验证仍需要固定 HTTPS 地址。

V3.6 不包含 JSON 导入导出、固定 HTTPS 发布、云同步、提醒或新的业务功能。

V3.7 JSON 导入导出已完成：

- 导出格式固定为包含 `app`、`export_version`、`schema_version`、`exported_at`、`source`、`storage_key` 和 `records` 的 JSON 结构。
- 导出只包含 `hydration_tracker_v3_records` 对应的 HydrationTracker 记录，不包含 Service Worker 缓存或其他浏览器数据。
- 导入前会校验 `app`、`export_version`、`schema_version`、`storage_key`、`source` 和每条记录的核心字段。
- 导入方式本轮使用“替换当前本机数据”，并要求二次确认。
- 导入成功后，运行时 localStorage 仍只保存 `{ schema_version, records }`。
- 导入导出与 Service Worker 缓存彻底分开；Service Worker 仍只缓存静态资源。
- JSON 备份主要用于换手机、迁移和恢复，不用于云同步。

V3.7 不包含固定 HTTPS 发布、云同步、提醒或新的业务功能。

V3.8 已完成，并已通过真实 iPhone Safari 手动测试：

- PWA 使用单个 `index.html` 和底部导航切换“今日 / 历史 / 备份”三个视图。
- “今日”视图只保留今日概览、添加记录、今日明细及今日删除和清空操作。
- 历史记录从首页移到独立“历史”视图，数据直接读取现有 `hydration_tracker_v3_records` 中的 `records`。
- 历史视图提供当前月份月历、有记录日期标记、月份切换和指定日期明细。
- 历史视图使用原生 SVG 展示近 7 日水分折线图及默认 `2000 ml` 目标线。
- 近 7 日趋势图不使用第三方图表库。
- JSON 导入导出从首页移到独立“备份”视图，原有校验、替换导入和二次确认保持不变。
- 本阶段不改变 localStorage key、`schema_version` 或 JSON 导入导出格式。
- 历史数据管理第一步已完成：支持按日期和记录 `id` 精确删除历史单条记录，并要求二次确认。
- V3.8 指定日期补录已完成，并已通过真实 iPhone Safari 手动测试。
- 历史视图选中日期后可点击“补录这一天”，复用常用项目库和估算规则，将月历选中日期写入 `date`，并将用户通过 `HH:MM` 时间控件填写的时间写入 `time`。
- 补录表单支持类型、常用项目、数量、餐次和可选备注；保存成功后刷新月历、选中日期明细和近 7 日趋势图。如果补录日期是今天，也会同步刷新今日概览和今日明细。
- V3.8 清空指定日期已完成：历史日期明细提供“清空这一天”，确认文案明确显示日期和记录数量，并只删除该日期记录。
- 历史记录目前支持查看、指定日期补录、单条删除和清空指定日期。
- 今日单条删除、清空今日、历史单条删除和清空指定日期等删除类操作均要求二次确认。
- 旧数据清理暂不实现，不再作为 V3.8 必做项，仅保留为未来可选增强。
- 下一阶段是 V3.9：固定 HTTPS 发布方式研究。

V3 的方向正式调整为 **iPhone 独立 PWA 原型**。不再以“iPhone 连接 Mac 上运行的 V2 Web App”为目标。

## 产品目标

HydrationTracker 最终应成为可以在 iPhone 上独立使用的简单水分记录工具。

日常使用要求：

- 日常记录只在 iPhone 上完成。
- 不依赖 Mac 开机或运行服务器。
- 不要求 iPhone 与 Mac 位于同一个 Wi-Fi。
- 不要求 iPhone 与 Mac 使用同一个 Apple ID。
- 不依赖 iCloud。
- 不需要 HydrationTracker 账号。
- 不做云同步。
- 尽量支持离线使用。
- 可以通过 Safari 打开，未来可以添加到 iPhone 主屏幕。
- 用户记录优先保存在 iPhone 浏览器本地。

开发和升级要求：

- Mac 继续用于修改代码、运行测试和生成新版本。
- iPhone 用于日常使用并保存用户记录。
- 更新网页代码后，iPhone 应继续读取原来的本地数据。
- 后续需要稳定的网址、缓存更新策略、数据结构兼容和 JSON 导入导出。

## 为什么 V2 架构不能满足目标

V2 是为 Mac 本地验证设计的 Web App：

- 页面依赖 Python `http.server` 后端。
- 计算、项目库和 JSON 读写主要由 Python 执行。
- 数据保存在 Mac 的 `data/hydration_log.json`。
- iPhone 若访问 V2，需要 Mac 开机并持续运行服务器。
- iPhone 通常还需要与 Mac 位于同一个局域网，并能够访问 Mac 的地址和端口。

这套方式适合开发和本地测试，但不符合“随时随地只用 iPhone 记录”的目标。V2 应保留为已完成的 Mac 本地版本，V3 建立独立的新前端目录，不破坏 V1/V2。

## V3 推荐技术路线

V3 推荐改造成纯前端 PWA：

- 使用原生 HTML、CSS 和 JavaScript。
- 日常运行不依赖 Python 后端。
- 把水分计算规则迁移到浏览器端。
- 把常用食物和饮品库迁移到浏览器端。
- 使用浏览器本地存储保存记录。
- 使用 Service Worker 缓存应用静态文件，提供基础离线能力。
- 使用 Web App Manifest 描述主屏幕名称、图标和显示方式。
- 通过固定 HTTPS 网址让 iPhone Safari 访问。
- Mac 继续作为开发、测试和发布环境。

Python V1/V2 可以继续作为计算结果和数据格式的参考实现，但不能成为 iPhone 日常运行的依赖。

## 建议文件结构

```text
HydrationTracker/
└── pwa/
    ├── index.html
    ├── styles.css
    ├── app.js
    ├── manifest.json
    ├── service-worker.js
    └── icons/
        ├── icon-192.png
        ├── icon-512.png
        └── apple-touch-icon.png
```

各文件职责：

- `pwa/index.html`：页面结构、表单、今日概览、记录明细和 PWA 基础 meta 配置。
- `pwa/styles.css`：布局、触控尺寸、iPhone Safari 适配和主屏幕模式样式。
- `pwa/app.js`：常用项目库、计算逻辑、本地数据读写、记录操作、数据迁移和页面交互。
- `pwa/manifest.json`：应用名称、启动地址、显示模式、主题颜色和图标声明。
- `pwa/service-worker.js`：缓存应用静态文件、支持基础离线启动并管理代码缓存版本。
- `pwa/icons/`：Safari 主屏幕和 PWA 使用的本地图标资源。

V3.2 初期可以保持单个 `app.js`，避免过早拆分。文件明显变大后，再按计算、存储和界面职责拆分模块。

## 浏览器本地数据方案

### localStorage

优点：

- 浏览器原生支持，不需要依赖。
- API 简单，适合新手理解和维护。
- 对少量结构化饮水记录足够直接。
- 页面刷新、代码更新和离线重开后可以继续读取。

限制：

- 只能保存字符串，需要使用 JSON 序列化。
- 同步读写，不适合大量数据或复杂查询。
- 缺少事务能力。
- 用户清除网站数据、浏览器回收存储或更换网址来源时，数据可能丢失或无法访问。

结论：**localStorage 足够支撑 V3 原型。** HydrationTracker 的单条记录较小，V3 也暂不做复杂历史统计。必须控制存储格式、捕获读写失败，并配套 JSON 导出。

### IndexedDB

IndexedDB 更适合以下情况：

- 记录量显著增加，需要按日期或其他字段查询。
- 需要事务、索引或更可靠的批量更新。
- 需要保存较大对象或更多类型的数据。
- 历史统计变复杂，localStorage 的整包读写开始影响体验。

V3 原型不应一开始使用 IndexedDB。可以先定义稳定的数据访问函数，让底层以后从 localStorage 迁移到 IndexedDB 时不必重写页面逻辑。

### JSON 导入和导出

JSON 导入导出不是云同步，而是由用户主动控制的本地文件备份和迁移方式。

它对以下场景很重要：

- 定期备份 iPhone 中的记录。
- 更换 iPhone 后恢复数据。
- Safari 网站数据被清除后恢复数据。
- 固定网址或托管平台发生变化时迁移到新的来源。
- 把 Mac V1/V2 的 JSON 记录迁移到 iPhone。
- 在升级数据结构前保留可恢复副本。

当前导入时必须校验文件格式、`schema_version`、记录字段和重复 `id`。V3.7 先实现“覆盖导入”，即用备份文件替换当前本机记录，并要求二次确认。

## 建议数据容器

localStorage 使用稳定 key，例如：

```text
hydration_tracker_v3_records
```

不要因每次代码升级而更换这个 key。数据内部保存版本号：

```json
{
  "schema_version": 1,
  "records": []
}
```

说明：

- `schema_version` 表示数据结构版本，不是应用代码版本。
- `records` 尽量保持与 V1/V2 兼容，包括 `id`、日期、时间、类别、名称、原始数量和单位、换算值、含水率、估算水分及备注。
- 应通过统一的 `loadData()`、`saveData()` 和迁移函数访问存储，页面代码不直接散落调用 localStorage。
- 应拒绝无法识别的新版本数据，避免静默覆盖。

## 程序更新与数据保留

程序代码和用户数据是两类不同内容：

- HTML、CSS、JavaScript、manifest 和 Service Worker 是应用代码，由 Mac 更新并发布。
- 用户记录保存在 iPhone 对应网页来源的浏览器存储中。

只要以下条件保持稳定，更新网页代码通常不应清空 iPhone 数据：

- 网页来源保持稳定，尤其是协议、域名和端口不变。
- localStorage key 保持稳定。
- 新代码继续识别旧的 `schema_version`。
- 更新流程不调用 `localStorage.clear()`，也不无条件覆盖现有数据。

需要注意：

- 仅保持页面路径相同不够，浏览器存储主要按来源隔离。更换域名、协议或端口可能得到新的空存储。
- Service Worker 的缓存版本与数据 `schema_version` 必须分开管理。更新应用缓存不应删除用户数据。
- 修改数据结构时，先读取旧版本，验证并迁移到新版本，再保存。
- 迁移逻辑应可重复执行，并在失败时保留原数据。
- 大版本升级前应提示用户先导出 JSON。
- localStorage 不是永久备份。用户清除 Safari 网站数据、设备存储压力或浏览器策略都可能影响数据，因此必须提供导出能力。

## 基础离线策略

- iPhone 第一次打开固定网址时需要联网下载应用文件。
- Service Worker 安装后缓存 `index.html`、CSS、JavaScript、manifest 和图标等静态资源。
- 后续在无网络时尽量从缓存启动。
- 用户记录读取和保存只使用浏览器本地存储，不依赖网络。
- 缓存更新采用明确的应用缓存版本，避免长期停留在旧代码。
- 不把用户记录写入 Service Worker Cache Storage，也不读取或修改 localStorage。
- 发布新版本后应显示简单更新提示，避免用户在操作过程中突然切换版本。

离线能力需要在真实 iPhone Safari 和主屏幕模式中验证，不能只依赖桌面浏览器测试。

## 发布和访问方式比较

### A. Mac 本地临时预览

适合：

- 开发页面和计算逻辑。
- 在 Mac 浏览器中快速测试。
- 发布前检查静态文件。

不适合日常 iPhone 使用，因为它仍依赖 Mac 开机、服务器运行和网络可达。

### B. 静态网页托管

例如 GitHub Pages、Netlify 或 Vercel。

优点：

- 提供固定 HTTPS 网址，适合 Safari 和 Service Worker。
- iPhone 不依赖 Mac 开机。
- Mac 发布新版本时只更新静态网页代码。
- 应用不需要账号系统或数据后端。
- 用户记录仍保存在 iPhone 本地，不提交到托管服务器。

注意事项：

- 首次访问和获取程序更新需要联网。
- 托管服务仍会处理普通网页请求，但应用不得把饮水记录发送给服务器。
- 更换托管域名会改变浏览器存储来源，迁移前必须先导出 JSON。
- 需要确认 Service Worker 的作用范围、缓存路径和静态资源路径。

推荐把静态托管作为 V3 日常使用的发布方向，但在 V3.9 再选择具体平台。

### C. 原生 iOS App

原生 App 可以作为远期备选，但当前不使用 Swift、不配置 App Store，也不把它作为 V3 路线。

## V3 分阶段计划

### V3.1：PWA 方案设计与路线图调整

- 明确 iPhone 独立使用目标。
- 确定纯前端 PWA、本地存储和静态托管方向。
- 明确更新、兼容和备份原则。

### V3.2：创建 `pwa/` 纯前端最小原型（已完成）

- 创建独立目录和基础页面。
- 先显示静态今日概览与添加表单结构。
- 不连接 Python 后端，不影响 V1/V2。

### V3.3：迁移项目库和计算逻辑（已完成）

- 把常用食物和饮品库迁移到 JavaScript。
- 迁移水分估算、今日总量、完成率和剩余量计算。
- 使用固定示例与 Python 结果做一致性验证。

### V3.4：使用 localStorage 管理记录（已完成）

- 保存和读取记录。
- 删除单条记录。
- 清空今日记录并保留历史日期。
- 加入稳定 key、`schema_version` 和输入校验。
- JSON 损坏或版本不支持时停止写入，避免覆盖原数据。
- 只操作 HydrationTracker 自己的 key，不调用 `localStorage.clear()`。

### V3.5：适配 iPhone Safari（已完成）

- 检查窄屏布局、安全区域和文字尺寸。
- 优化表单、触控尺寸、确认流程和键盘输入。
- 布局与交互优化完成后，仍建议在真实 iPhone Safari 中手动测试。
- 保持 V3.4 的 localStorage 数据结构和记录管理行为不变。
- 增加目标完成率进度环和六档鼓励提示。
- 增加项目 emoji，并修复“今日明细”标题在窄屏下换行的问题。
- 修复取消确认后危险按钮颜色残留，并在保存成功后将餐次恢复为“无餐次”。
- V3.4 的保存、读取、单条删除和清空今日功能保持不变。
- 常用项目库扩展和自定义记录仅完成需求登记，自定义记录尚未实现。
- 页面美化和视觉反馈属于 V3.5 范围，不提前加入 V3.6 的 PWA 缓存能力。

V3.7 完成后的下一阶段是 V3.8：历史记录查看与历史数据管理。

### V3.6：添加 PWA 和基础离线能力（已完成）

- 添加 manifest、图标和主屏幕显示配置。
- manifest 和图标已独立补齐，适合作为后续主屏幕安装基础。
- 添加 Service Worker 和应用静态资源缓存。
- 设计缓存版本与更新提示。
- Service Worker 只缓存应用代码资源，不缓存用户本地记录，也不负责保存用户数据。
- Service Worker 涉及缓存生命周期和代码更新控制，必须避免旧版本长期滞留。
- Service Worker 通常需要 HTTPS；部分浏览器仅对本地开发来源提供例外。
- iPhone Safari 临时测试已通过：页面可从局域网地址打开，可添加到主屏幕，并像轻量小工具一样启动。
- 主屏幕 Web App 与 Safari 普通标签页的本地数据不应默认视为同一份数据。
- 当前局域网地址只用于开发阶段临时测试，不用于最终发布。
- 直接打开 `pwa/index.html` 的 `file://` 方式不能完整注册和验证 Service Worker。
- Service Worker 缓存版本与 localStorage `schema_version` 分开管理。
- 最终的离线启动、缓存更新和数据保留验证应在固定 HTTPS 网址发布后进行。

### V3.7：实现 JSON 导入和导出（已完成）

- 导出格式固定为：`app`、`export_version`、`schema_version`、`exported_at`、`source`、`storage_key` 和 `records`。
- 导出文件名使用 `hydration-tracker-backup-YYYY-MM-DD.json`。
- 导入前校验 JSON 解析、应用标识、导出版本、数据版本、storage key 和记录字段。
- 导入方式当前使用替换当前本机数据，并要求二次确认。
- 导入成功后仍写回 `{ schema_version, records }`，不把导出元数据混入运行时数据。
- JSON 备份用于换手机、迁移和恢复；与 Service Worker 缓存彻底分开。

### V3.8：页面结构重组与历史记录管理（已完成）

当前历史记录已经保存在 `hydration_tracker_v3_records` 的 `records` 数组中。V3.8 将今日、历史和备份职责拆分为三个独立视图，避免所有功能继续堆在首页。

当前页面结构：

- “今日”视图：今日概览、进度环、鼓励提示、添加记录、今日明细、今日单条删除和清空今日。
- “历史”视图：历史月历、月份切换、日期总水分标记、指定日期明细、指定日期补录、历史单条删除、清空指定日期和近 7 日折线图。
- “备份”视图：JSON 导出备份、JSON 导入恢复/迁移以及本地数据边界说明。

三个视图继续共享同一份 localStorage records。导航仅切换显示内容，不创建新数据容器，也不改变数据。

页面结构重组已在真实 iPhone Safari 上验证通过，底部导航、月历、月份切换、日期明细和趋势图可以正常使用。

历史记录查看与管理已完成：

- 月历默认显示当前月份，并可切换上一个月或下一个月。
- 有记录日期显示当天总水分，点击任意日期可查看该日明细；无记录日期显示空状态。
- 近 7 日折线图按日期展示每天总水分，无记录日期补 `0 ml`，并显示默认目标线。
- 折线图使用原生 SVG 绘制，不安装或加载第三方图表库。
- 选择今天或过去日期后，可以展开补录表单，填写类型、常用项目、数量、餐次、`HH:MM` 时间和可选备注。
- 补录记录沿用现有 record 结构，`date` 使用月历选中日期，`time` 使用用户输入时间，不升级 `schema_version`。
- 补录成功后统一刷新今日概览、今日明细、历史月历、当前日期明细和近 7 日趋势；非今天补录不改变今日统计。
- 历史明细中的每条记录提供危险样式删除按钮，删除前显示包含日期和记录名称的二次确认。
- 删除仅匹配同一 `date` 和记录 `id` 的一条记录；取消确认、记录不存在或写入失败时不修改现有数据。
- 删除成功后统一刷新今日概览、今日明细、历史月历、当前日期明细和近 7 日趋势图。
- 添加、今日删除或清空、JSON 导入完成后，月历、趋势图和日期明细会随统一页面刷新同步更新。

V3.8 清空指定日期已实现：

- 历史日期明细只在该日有记录时显示“清空这一天”。
- 清空前统计选中日期记录数量，并在二次确认文案中显示日期和数量。
- 确认后仅删除 `date` 等于选中日期的记录；取消确认时不修改数据。
- 清空后刷新历史月历、选中日期明细和近 7 日趋势；清空今天时也同步刷新今日概览和今日明细。
- 历史单条删除和清空指定日期均必须二次确认。

未来可选增强：

- 旧数据清理暂不实现。未来如确有需要，可考虑删除 30 天前、90 天前或指定日期以前的记录，并要求明确的二次确认。
- 历史读取和管理继续使用同一个 localStorage key：`hydration_tracker_v3_records`。
- 默认保持 `schema_version: 1`；只有数据结构确实需要变化时才设计迁移并升级版本。
- 不调用 `localStorage.clear()`，所有删除操作只修改 HydrationTracker 自己的 `records`。
- 不改变 V3.7 JSON 导入导出格式；导入导出仍覆盖完整 `records` 数据。
- 不改变 Service Worker 边界；Service Worker 仍只缓存静态资源，不读取、缓存或修改用户记录。

V3.8 至此正式完成。下一阶段是 V3.9：研究固定 HTTPS 发布方式，让 iPhone 和家人设备能够通过稳定网址访问应用，同时继续将各自记录保存在各自设备本地。

### V3.9：固定 HTTPS 发布方式研究（已开始）

当前阶段只研究和设计发布方案，不创建线上站点，不上传代码，不配置域名，也不修改 PWA 功能代码。当前正式项目目录尚未初始化为 Git 仓库；实际发布准备应在方案确认后单独进行。

#### 方案比较

| 方案 | 纯前端 PWA 与 HTTPS | 固定网址和更新方式 | 新手体验 | 主要注意事项 |
| --- | --- | --- | --- | --- |
| GitHub Pages | 非常适合直接托管 HTML、CSS、JavaScript、manifest、Service Worker 和图标。默认 `github.io` 地址及正确配置的自定义域名都支持 HTTPS。 | 项目站点通常使用 `https://<用户名>.github.io/<仓库名>/`。可从分支根目录或 `/docs` 发布，也可用 GitHub Actions 发布静态目录；后续推送更新即可重新部署。 | 适合个人项目，流程清晰，不需要安装运行时或维护服务器。 | GitHub Free 通常需要公开仓库，Pages 站点本身公开。当前 `pwa/` 不是分支发布支持的根目录或 `/docs`，因此应使用 GitHub Actions 只上传 `pwa/` 目录作为 Pages artifact。绝不能把 `data/hydration_log.json`、凭据或其他个人文件上传。 |
| Netlify | 非常适合静态 PWA。所有站点提供 HTTPS，默认 `netlify.app` 地址和自定义域名都可使用自动证书。 | 可连接 Git 仓库自动部署，也可通过网页上传静态目录。生产站点使用固定主网址，更新后产生新的原子部署。 | 网页向导直观，首次部署通常较容易。 | 需要额外的 Netlify 账号和项目配置。应固定生产站点名称或自定义域名，不能把 Deploy Preview 临时地址当作日常网址。平台套餐和限制可能变化，正式发布前需要重新核对。 |
| Vercel | 能托管纯静态文件，项目会获得 `vercel.app` 生产域名；加入项目的域名会自动尝试配置 SSL 证书。 | 常见方式是连接 Git 仓库，每次推送自动部署；也支持 CLI。应使用生产域名，不使用每次部署生成的预览网址。 | Git 集成方便，但平台能力明显超过本项目当前需求。 | CLI 路线需要额外安装工具，本项目没有必要使用。预览地址与生产地址容易混淆，项目和域名配置也比纯静态需求更复杂。 |
| Mac 局域网临时服务器 | 可以测试页面，但通常只是 `http://Mac局域网IP:端口`，不是稳定的公网 HTTPS 来源。 | Mac IP、端口或网络可能变化；Mac 必须开机并持续运行服务器。 | 适合当前开发调试。 | iPhone 必须与 Mac 位于可访问的局域网，家人异地无法使用，不适合作为主屏幕 Web App 的长期来源，也不能代表最终 HTTPS 和离线更新环境。 |

官方资料：

- [GitHub Pages 是静态站点托管服务](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [GitHub Pages 发布来源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [GitHub Pages HTTPS 支持](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)
- [Netlify 从 Git 仓库部署](https://docs.netlify.com/start/quickstarts/deploy-from-repository/)
- [Netlify HTTPS 和自动证书](https://docs.netlify.com/manage/domains/secure-domains-with-https/https-ssl/)
- [Vercel 部署方式](https://vercel.com/docs/deployments/overview)
- [Vercel 域名和 SSL](https://vercel.com/docs/domains/working-with-ssl)

#### 推荐路线

推荐优先使用 **GitHub Pages**，继续使用当前 `hydration-tracker` 仓库，并通过 GitHub Actions 只发布经过检查的 `pwa/` 静态文件。

推荐理由：

- HydrationTracker PWA 已经是无构建步骤的原生 HTML、CSS 和 JavaScript，完全符合 GitHub Pages 的静态托管定位。
- 默认提供固定 HTTPS 项目网址，适合 Safari、Service Worker 和添加到主屏幕。
- 更新方式可以保持简单：在 Mac 完成开发与测试后，只把确认过的 PWA 静态文件更新到发布仓库。
- 不需要 Python 后端、服务器维护、云数据库或第三方 CLI。
- 发布代码与本地开发目录分开，可以明确阻止 `data/hydration_log.json` 和其他不应公开的文件被上传。

建议初期使用固定的 GitHub Pages 项目网址，例如 `https://<用户名>.github.io/hydration-tracker/`。仓库名、GitHub 用户名和发布来源确定后不要随意更改。自定义域名可作为以后进一步提高网址独立性的选项，但应在积累长期数据前决定；切换域名仍需要按新来源迁移本地数据。

Netlify 是第二选择：如果用户更偏好网页拖放或可视化部署向导，可以使用固定的生产 `netlify.app` 地址。Vercel 也可用，但其预览、构建和全栈能力对当前纯静态项目没有明显收益。

#### 发布网址与 iPhone 本地数据

应用代码由固定 HTTPS 网址提供，但用户记录仍只保存在每台设备自己的 localStorage 中。托管平台只保存公开的静态应用文件，不接收 HydrationTracker 记录。

浏览器存储主要按来源隔离，即协议、主机名和端口共同决定数据空间：

- 旧局域网 `http://192.168.x.x:8001` 与新 HTTPS 地址一定是不同来源。
- 更换 GitHub 用户名、托管平台或自定义域名通常会得到新的来源。
- 即使页面内容相同，新来源也不会自动获得旧来源的 localStorage。
- Safari 普通标签页和主屏幕 Web App 的数据也不应被假定为完全共享。
- 家人设备访问同一网址后会建立各自的本地数据，不会与其他设备自动同步。

因此，JSON 导出和导入是发布迁移的必要步骤：先从实际保存记录的旧环境导出备份，再在新固定 HTTPS 地址中导入。导入仍是替换新来源当前数据，不是合并。

#### 发布前检查清单

1. 在当前实际使用的主屏幕 Web App 中先导出 JSON 备份；如果 Safari 普通标签页也有独立数据，应分别导出需要保留的备份。
2. 核对备份文件名、记录数量和文件可读取性，并保留原文件，不直接覆盖。
3. 确认 localStorage key 仍为 `hydration_tracker_v3_records`。
4. 确认 `schema_version` 仍为 `1`。
5. 再次验证 JSON 导出与替换导入流程。
6. 确认 Service Worker 静态缓存版本与数据 `schema_version` 分开管理。
7. 确认应用和 Service Worker 都不调用 `localStorage.clear()`。
8. 确认 Service Worker 只缓存静态资源，不读取、缓存或修改用户记录。
9. 只发布 `pwa/` 中经过检查的静态资源；不得上传 `data/hydration_log.json`、密码、令牌、环境文件或其他个人文件。
10. 先确定最终生产网址，不使用预览网址、临时部署网址或局域网地址作为长期入口。
11. 不假设 Safari 标签页、主屏幕 Web App、旧局域网地址和新 HTTPS 地址会自动共享数据。

#### 发布后验证清单

1. 固定 HTTPS 网址可以正常打开，没有证书或混合内容错误。
2. iPhone Safari 可以添加到主屏幕，名称和图标正确。
3. 从主屏幕打开后使用独立显示模式，布局和触控正常。
4. 添加、今日删除、历史单条删除、指定日期补录、清空今日、清空指定日期、历史月历、趋势图及备份功能正常。
5. 在同一固定网址下关闭并重新打开后，localStorage 记录仍能读取。
6. 更新静态代码后，Service Worker 能取得新版本，不长期停留在旧缓存，也不触碰用户数据。
7. 首次在线加载后，验证基础离线启动是否正常。
8. 从旧环境导出的 JSON 可以在新固定网址中通过二次确认正常导入。
9. 导入后今日、历史和备份视图显示正确，并能继续添加、删除和导出。
10. 家人设备可以打开同一网址并独立使用；各设备记录只保存在各自本地，不自动共享。

V3.9 当前只完成方案研究。没有创建仓库、上传文件、配置域名或实际发布。

#### GitHub Pages 发布准备（已开始）

发布目标已经确定：

- GitHub 用户名：`Rocksheep27`
- 仓库名：`hydration-tracker`
- 远程仓库：`https://github.com/Rocksheep27/hydration-tracker.git`
- 预计 Pages 地址：`https://rocksheep27.github.io/hydration-tracker/`

当前本地状态：

- 正式项目路径为 `/Users/hhxx/Documents/CodexProjects/HydrationTracker`。
- 本地 Git 初始化已完成，当前分支为 `main`。
- `origin` 已设置为 `https://github.com/Rocksheep27/hydration-tracker.git`。
- `git ls-remote --heads origin` 未返回远程分支，远程仓库目前看起来为空。
- 首次本地提交和首次推送已完成，但尚未开启 GitHub Pages。
- `data/hydration_log.json` 当前包含本地记录，必须保留在 Mac，不能提交或上传。
- 根目录 `.gitignore` 已排除本地记录、JSON 备份、环境文件、Python 缓存和 macOS 本地文件。

建议提交到源代码仓库：

- `.gitignore`
- `AGENTS.md`、`README.md`
- `docs/`
- `pwa/`
- `src/`、`tests/`、`web/`
- `data/.gitkeep`

不应提交：

- `data/hydration_log.json`
- `hydration-tracker-backup-*.json`
- `.env`、令牌、凭据或私钥
- `.DS_Store`、`.Rhistory`
- `__pycache__/`、`*.pyc` 和本地虚拟环境

GitHub Pages 实际发布内容仍然只应来自 `pwa/`。源代码仓库可以保存 V1、V2、V3 的安全代码和文档，但 Pages 部署产物不能包含 `data/`、`src/` 或其他非 PWA 文件。

#### 子路径兼容性检查

目标页面位于仓库子路径 `/hydration-tracker/`。当前 PWA 路径检查结果：

- `index.html` 使用 `styles.css`、`app.js`、`./manifest.json` 和 `./icons/...` 等相对路径。
- manifest 使用 `"start_url": "./index.html"` 和 `"scope": "./"`，发布后会解析到 `/hydration-tracker/index.html` 和 `/hydration-tracker/`。
- manifest 图标使用 `./icons/...`，不会跳到网站根目录。
- Service Worker 使用 `./service-worker.js` 注册，默认作用域为 `/hydration-tracker/`。
- Service Worker 的静态缓存列表全部使用 `./...`，会在当前 Pages 子路径内解析。
- 未发现写死为网站根路径 `/styles.css`、`/app.js`、`/manifest.json` 或 `/icons/...` 的资源引用。
- Service Worker 仍只缓存静态文件，不读取、不缓存、不修改用户记录，也不调用 `localStorage.clear()`。

结论：当前 PWA 静态资源适合部署到 `https://rocksheep27.github.io/hydration-tracker/`，manifest 和 Service Worker 没有需要立即修改的子路径风险。

GitHub Pages 的分支发布来源只支持分支根目录或 `/docs`，不能直接选择当前的 `pwa/`。因此本项目改用 GitHub Actions，把 `pwa/` 作为 Pages artifact 上传并部署。

#### GitHub Pages Actions 部署配置阶段

- 已新增 `.github/workflows/deploy-pages.yml`。
- 工作流使用 GitHub 官方 Pages Actions：
  - `actions/checkout`
  - `actions/configure-pages`
  - `actions/upload-pages-artifact`
  - `actions/deploy-pages`
- `upload-pages-artifact` 的发布路径固定为 `pwa`，因此 Pages 产物只包含 PWA 静态文件。
- `data/hydration_log.json`、`src/`、`tests/`、`web/` 和其他非 PWA 文件不会作为 GitHub Pages 页面内容发布。
- 当前预计访问网址保持为 `https://rocksheep27.github.io/hydration-tracker/`。
- 发布前已提醒先从当前 iPhone 主屏幕 Web App 导出 JSON 备份。
- GitHub Pages 新网址与旧局域网测试地址属于不同来源，localStorage 不会自动共享。
- 首次部署后，需要在新网址中通过“备份”视图导入旧 JSON 数据。
- 发布后需要重点验证：
  1. Service Worker 更新是否正常获取新版本。
  2. 主屏幕模式是否能稳定打开。
  3. 基础离线启动是否正常。
  4. JSON 导入后今日、历史和备份三视图是否同步刷新。

#### 首次本地提交阶段

- 已完成 `git init`、`main` 分支设置、`origin` 配置和远程分支只读检查。
- 暂存前已确认本地 JSON、备份、缓存和系统文件均被 `.gitignore` 排除。
- 首次提交只包含经过检查的项目规则、文档、PWA、V1/V2 源码、测试和 `data/.gitkeep`。
- 首次本地提交已完成，提交信息为 `Initial commit for HydrationTracker PWA`。
- 首次推送已完成，当前远程仓库已存在 `refs/heads/main`。
- 下一步是在 GitHub 网页端选择 GitHub Actions 作为 Pages 发布来源，并让首次 workflow 运行完成。

#### 首次发布前的数据迁移

1. 先在当前真实使用的 iPhone 主屏幕 Web App 中导出 JSON 备份。
2. 当前局域网地址与 `https://rocksheep27.github.io/hydration-tracker/` 是不同来源，localStorage 不会自动迁移。
3. 固定 HTTPS 页面发布后，先打开新网址并检查空数据状态。
4. 再通过“备份”视图导入旧 JSON；导入会替换新网址下的当前本机记录。
5. localStorage key 保持 `hydration_tracker_v3_records`，`schema_version` 保持 `1`，JSON 导入导出格式保持不变。

## V3 暂不实现

- 不做提醒通知。
- 不做云同步。
- 不做账号系统。
- 不做 iCloud。
- 不做 App Store 发布。
- 不做原生 iOS App。
- V3.8 只做基础历史汇总和按日期管理，不做复杂图表或深度统计分析。
- 不做每日目标个性化设置。
- 不做按时间进度判断补水建议。

这些增强功能保留到 V4 或更后阶段。

## 未来项目库与自定义记录

### 扩展常用项目库

常用项目库允许在后续小版本中持续补充新的常吃食物和饮品。每个新增项目应包含：

- `id`
- `name`
- `category`
- `default_unit`
- `default_amount`
- `base_type`
- `water_ratio`
- `emoji`

兼容原则：

- 新增项目只扩展项目库，不修改已有项目 ID 或旧记录结构。
- 已保存记录继续优先根据 `item_id` 匹配；无法匹配时根据 `name` 回退显示。
- 显示用 emoji 不要求写入旧记录，也不参与水分计算。
- 扩展常用项目库可作为后续 V3 或 V4 的小版本更新逐步进行。

### 自定义食物和饮品记录

未来可以允许用户记录常用项目库以外的食物或饮品，考虑两种输入方式：

1. 直接输入估算水分，例如“火锅 1 份，估算 500 ml 水分”。
2. 输入重量或容量和含水率，由程序计算估算水分。

自定义记录应保存用户输入的名称、单位、数量、估算水分和备注，并遵守以下边界：

- 自定义记录不修改或污染内置常用项目库。
- 如果以后支持“保存为常用项目”，需要单独设计校验、重复 ID、编辑和删除规则。
- 自定义数据更依赖可靠备份和迁移，因此建议放入 V4，或至少等 V3.7 JSON 导入导出完成后再实现。
- 实现前需要设计向后兼容的数据迁移，不得使现有 `schema_version: 1` 记录失效。

以上两项本轮仅记录需求，不属于 V3.5 已实现功能，也不改变当前 localStorage key 或数据结构。

## V3 实施的固定决策

各阶段实现时保持以下约定：

1. localStorage key 使用 `hydration_tracker_v3_records`。
2. 初始 `schema_version` 使用整数 `1`。
3. V3 不读取或修改现有 Mac `data/hydration_log.json`。
4. PWA 记录字段尽量兼容 V1/V2。
5. 前端计算结果必须用现有示例数据与 Python 版本交叉验证。
6. Service Worker、发布和数据导入导出按路线图分阶段实现，不提前混入当前阶段。
