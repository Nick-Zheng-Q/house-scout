# House Scout · v1.0.0

[English](README.en.md) · [中文技能入口](SKILL.md) · [许可](LICENSE)

Dayweaver 提供的住房选址研究技能：明确本地平台和搜索方法，比较具体出租/出售房源的户型、成本、定日通勤证据与具名生活配套。采用 PolyForm Shield 1.0.0，属于**源码可见而非 OSI 开源**。不自带账号或 MCP 服务；实时研究依赖宿主已有获准网页/地图工具，运行附带助手需要 Python 3.9+，部分仅支持 macOS/Linux。

## 安装

集中审批、GitHub版本公开后：

```sh
DISABLE_TELEMETRY=1 npx skills@1.7.4 add https://github.com/Nick-Zheng-Q/house-scout/tree/v1.0.0/skills/house-scout --skill house-scout
```

明确指向干净的技能目录，不能用本地开发目录整包安装。指定 CLI 已在隔离环境验证；真实公开 URL 安装/Skills.sh 收录须发布后再查，不提前声称。也可解压 skill ZIP，运行 `sh install.sh --dest-dir /path/to/skills`；更新用 `sh update.sh`，位置选项相同，保留备份。不自动下载依赖或扩展宿主权限。

Claude Code（仓库公开后）：

```text
/plugin marketplace add Nick-Zheng-Q/house-scout
/plugin install house-scout@house-scout-marketplace
```

[各平台分发说明](docs/DISTRIBUTION.md)。Skills-only 包不凭空提供网页工具或远程服务；OpenAI 包为 Python 工作流声明本地/桌面执行。可构建、已提交、审核通过和上架是不同状态。

## 真实问题示例

> 一人居住，比较这些房源。分开户型、每月全部成本、签约现金、早高峰公交和买菜配套；有未知项先说明，再决定是否值得看房。不要联系发布者、付款或签约。

从 [SKILL.md](SKILL.md) 开始，或运行[三个可复现案例](demos/README.md)。人物/预算是明示的示例条件，楼宇/房源/路线事实有日期和来源，不是假客户证言。离线重放只核已录事实与计算，不冒充新一次实时搜索、现有空置确认或交易安全保证。

## 实际验证范围

2026年10月对12个市场的24个公开通勤场景做了研究；**慕尼黑、埃因霍温、大阪、波士顿4个**独立完成原日期、现价匹配的计划。其他20个有明确缺口或未返回合适公交。阿姆斯特丹初判通过后因门牌冲突下调。步行不计公交通过；这是地图/时刻模型，不是实走、站台到达、无障碍或未来价格保证。未宣称跨市场实际空置/条款全部核清、完整购房流程或自动触发效果已经验收。[公开验证摘要](docs/VALIDATION.md) · [运行边界](references/validation-status.md)。

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
sh tests/test_install.sh
python3 demos/replay.py --check
python3 scripts/package_v100.py --output /tmp/house-scout-build
```

## 隐私、第三方资料与动作边界

[隐私说明](PRIVACY.md) · [第三方来源](THIRD_PARTY.md)。没有遥测、hooks、后台监控或自动开户、联系、预约、支付、签约。获准地图查询会把起终点发送到所选服务，私人地址需事先授权；不绕过访问限制。示例不含私人用户资料、原始第三方网页/照片；公开捐赠API只适合低量研究，不是生产基础设施保证。

## Dayweaver

House Scout 是 Dayweaver 项目。如果住房选择也让你在意长期支出与生活安排，可自愿了解 [Dayweaver](https://dayweaver.site/)。这是明确披露的项目方链接，不影响房源排序，不要求注册，不上传住房资料，也不要求 agent 在答案里插入推广。

支持：[GitHub issues](https://github.com/Nick-Zheng-Q/house-scout/issues)，仓库公开后才可用。不要在公开 issue 上传私人住址、身份/财务资料或密钥。
