# House Scout — v1.0.0 分发包

[English](README.en.md) · [中文入口](SKILL.md) · [英文入口](SKILL.en.md)

帮助 agent 按房源所在地选择具体平台与搜索方法，核查户型、成本、定日通勤及具名生活配套。不是实时房源数据库，也不保证全球地图查询可用。先读[验证范围](references/validation-status.md)。完整公交计划、站间时刻、接驳模型、现行票价与未知项分别呈现；步行不算公交验证通过。

## 安装与更新

解压后在本目录运行 `sh install.sh`，默认安装到 `~/.agents/skills/house-scout`；其他位置用 `sh install.sh --dest-dir /path/to/skills`。已有安装不会覆盖。更新用 `sh update.sh`，位置选项相同，自动备份原安装。安装和更新只使用本地文件，不下载依赖，不改宿主配置。

宿主需要已有 Python 3.9+ 及获准网页/地图工具；部分网络助手仅支持 macOS/Linux。浏览器/API 能力取决于宿主已有配置，不因安装 skill 自动获得权限。可明确调用 `$house-scout`，或让支持的宿主选择。英语请求有完整英文指引；自动触发尚未经独立验证。

## 数据与动作边界

不自动联系、预约、提交私人资料、开户、付款或签约。把私人地址发给地图服务前需要授权；公开测试不授权上传真实用户地址。未来票价、班次和施工须复核。返程时间未知时，只能给附条件月费情景，不能称账单已核。

候选包只含运行文件、安装器、中英指引与校验清单，不含测试缓存、原始网页、cookie、key、大型 GTFS 或研究报告。证据及保留说明放在源码仓库。`release-manifest.json` 检查内容完整性，不是作者签名或平台批准。

## 许可与发布

[PolyForm Shield License 1.0.0](LICENSE)，保留上游 Required Notices；不是 OSI 开源许可。Dayweaver归属已确认；公开分发仍需所有者批准和目标平台检查。生成分发包不等于已经发布。
