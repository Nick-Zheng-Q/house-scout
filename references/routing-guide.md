# 地图界面不可用时：路线、票价与生活配套

**需要公共交通时：**执行[实际时段公交核查](transit-guide.md)，步行模型及配套路网不得计作公共交通验证。

每个保留房源在[户型核查](enrichment-guide.md)后使用。Google方向链接在文本读取工具里打不开，**不等于所有路线来源都不可用**。分别处理坐标、路网、公交时刻/票价、具名商户；可以交付有依据且标清范围的估计，不冒充高峰实测。

## 工具选择与访问错误

| 已有能力 | 具体操作 |
| --- | --- |
| 网页检索/读取（`web.run`、`web__run`或宿主对应工具） | 搜精确起终点、运营方时刻/票价表、Moovit/Rome2Rio线路页、商户官方门店定位器，打开支持结论的结果而非只看摘要。此工具不一定执行JavaScript或提交表单。 |
| 已有获准浏览器交互（浏览器工具**或宿主现成Playwright**） | 按工具说明，或用宿主依赖工具发现现成运行环境并按[Playwright方法](transit-guide.md)提交起终点、当地日期/时刻、方式，记录**返回行程**。仅能打开Codex浏览器标签不是可交互查询能力；不编工具名、不自动安装浏览器包。 |
| 获准终端/Python且能HTTPS联网 | 运行下方`scripts/query_routes.py`查询已文档化公开API，属于HTTP数据读取，不是浏览器自动化。沙箱DNS/联网拒绝要申请针对性联网批准，不误记为服务端故障，也不改用其他手段规避批准。 |
| 已有获准地图/交通连接器或API key | 按其文档用地理编码、路线、POI方法及坐标口径。从获准配置读取密钥，不公开写进报告或命令日志。API必须在查询参数传key时，对保存/展示的URL和请求元数据脱敏。任务不授权开户、付费或扩大权限。 |

网站明确封禁、401/403、429应核权限/密钥、退避或转独立来源，不改会话/伪装客户端绕过。技术性502/超时可延迟后有限重试一次，再换另一类来源；不轮换镜像逃限流。没有UI不能成为跳过HTTP及静态时刻表方案的理由。

## 可执行的公开地点助手

Python3标准库，支持macOS/Linux，不需要安装包或给助手配置账号/密钥。查询**Photon**候选坐标、**FOSSGIS OSRM步行后端**路网、**Overpass**小范围买菜/药店/商场点位，以及**VBB社区REST服务**的柏林/勃兰登堡行程。这些捐赠/演示/社区服务是可选方案，不是保证可用的基础设施。

使用前读[Photon演示/API](https://github.com/komoot/photon)、[FOSSGIS政策](https://routing.openstreetmap.de/about.html)、[Overpass政策](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html)、[VBB包装服务文档](https://v6.vbb.transport.rest/api.html)。助手用跨进程共享锁、请求间至少1.2秒、成功结果缓存一小时，**不自动重试**，同机subagent共享节流。仅小规模测试，复用缓存，不将公共端点部署成大规模应用后端。OSM结果标注来源并附[纠错链接](https://www.openstreetmap.org/)。**不默认接入公共Nominatim**：[其LLM/应用政策](https://operations.osmfoundation.org/policies/nominatim/)要求开发者知情负责并限制通用生成式查询服务，不能静默替换过去。

远端会记录请求。仅用公开模拟地点，或已明确获准向具体服务披露的位置。`--public-locations`是对此的确认，不是上传私人住址/工作地址的通用同意；公开房源地址不代表用户当前住址也可发送。

在已安装skill目录运行，全局选项放子命令**之前**。`--output`保存请求URL、抓取时间、缓存状态、原响应和摘要：

```sh
python3 scripts/query_routes.py --public-locations --output /tmp/place.json geocode "Old Street London" --tag railway:station
python3 scripts/query_routes.py --public-locations --output /tmp/walk.json walk --origin=51.5266,-0.0982 --destination=51.5257,-0.0875
python3 scripts/query_routes.py --public-locations --output /tmp/nearby.json pois --origin=51.5266,-0.0982 --radius 600
python3 scripts/query_routes.py --public-locations --output /tmp/berlin.json vbb --origin=52.507,13.322 --destination=52.525,13.369 --arrival=2026-12-01T09:00:00+01:00
```

这些只是公开演示点/命令，不默认是真实房源门口或已查实行程。`vbb`**只适用覆盖区域**，是社区包装而非VBB官方API，可能失败或返回其他日期。必须核返回起终点、所有接驳、提醒及`requested_arrival_date_and_deadline_match`；未返回价格即未知，不是免费。

### 坐标与步行路线

1. 从目标挂牌取得具体公开地址，确认目的地真实入口。Photon返回候选后核城市/国家、门牌、街道及**对象类型**。第一条“站名”可能是旧站、单车点或其他城市；`--tag railway:station`可缩小铁路查询，但不保证涵盖所有地铁/公交站。脚本不自动选第一条。
2. 助手输入为**WGS84纬度,经度**；Photon/OSRM GeoJSON为**经度,纬度**。不要颠倒，也不混用中国商业地图GCJ-02/BD-09而无核实转换/来源。楼宇中心或仅街道级挂牌须标近似，不能编门牌。
3. 去程、返程及选中的商户/公交接驳段分别跑`walk`。使用`/routed-foot/`而非汽车路由冒充步行。检查吸附坐标/偏移和路线街名，异常绕行/封闭边界需要复查。
4. 报路网距离、`model_minutes`，注明**非时刻化步行路网模型**、起终点精度、查询日和OSM来源；不含室内接驳、信号灯、实时封路、人流及未核无障碍。不能称执行了9点行程。可以据此解释45分钟偏好的估计比较，但不保证准点；该步行票价0仅指这段步行，不等于家庭交通总费0。

## 没有一体规划器时怎么查公交/地铁

有实际API/HTML行程就使用；否则组成**有来源的时刻表估计**：已查家门→上车点路网＋适用班次的候车＋车内时间＋有依据换乘步行/等待＋下车点→目的地路网。逐段保留来源/日期，从目标到达倒推应出发时间。资料未覆盖目标日期时注明参考工作日/日期、目标日待复核；不把静态平均写成指定时刻结果。缺段时交付已知段与明确部分估计，不编完整总时间。

| 市场 | Google/高德界面失败后去哪里 | 票价如何核 |
| --- | --- | --- |
| 中国大陆 | 已有获准key时用高德/百度**公开文档化API**；否则实际城市地铁站点/线路时刻表＋可读线路页。搜`"[小区/地址]" "[目的地]" 公交 地铁`及`site:moovitapp.com "[站名]" "[城市]"`；OSM坐标/道路覆盖适用时才用步行后端。 | 地铁运营方站到站票价或正式里程/票制，公交对应线路票价。Moovit附近线路列表不是门到门行程。 |
| 美国 | 实际城市SFMTA/Caltrain或MBTA线路时刻/GTFS下载；`site:moovitapp.com "[起点]" "[终点]"`或`site:rome2rio.com/s/ "[站A]" "[站B]"`。只有核日期、stop IDs、换乘路径后才用官方静态GTFS，不只加车内时长。 | 实际运营方票价/换乘/支付规则；跨铁路/巴士运营方分别核覆盖。明确robots拒绝的域名不换客户端重试。 |
| 英国 | 已获准且可用时用[TfL行程API](https://api.tfl.gov.uk/swagger/docs/v1)；其他地区Stagecoach/本地铁路时刻PDF；Moovit/Rome2Rio精确站对参考页。本次TfL API返回403，**不假定无key可用**。 | TfL/实际运营方票价器、区域、封顶和生效日，匹配线路/支付方式/时段。 |
| 加拿大 | [TransLink时刻/地图](https://www.translink.ca/schedules-and-maps)→具体SkyTrain/公交；TTC/GO线路PDF或官方GTFS；实际站对参考路线。 | TTC/GO/TransLink区域、换乘/封顶；官方网络费率＋未核行程不等于具体票价已确认。 |
| 澳大利亚 | Transport for NSW、Transport Victoria/PTV具体线路PDF或获准开放数据API＋步行接驳。搜`site:transportnsw.info "[线路/站]" timetable`或`site:transport.vic.gov.au "[线路]" timetable`。 | Opal/contactless或myki的方式/区域/工作日/生效日期，不套过期未来票价。 |
| 新西兰 | Auckland Transport / [Metlink](https://www.metlink.org.nz/) **具体线路时刻PDF**和地图，已有权限时用GTFS/数据，接驳另查。搜`"[线路]" "[站]" timetable site:at.govt.nz`或`site:metlink.org.nz`。 | AT HOP/contactless或Metlink分区/支付/日期/换乘；不未核覆盖就套月票。 |
| 新加坡 | 获准时用OneMap/LTA文档化API；否则SimplyGo/LTA**票价计算器及地铁/公交线路明细**、SMRT/SBS站点时刻、Moovit地点页＋步行接驳。 | [SimplyGo](https://www.simplygo.com.sg/)实际行程距离/换乘/支付；只打开计算器不是得到票价。 |
| 中国香港 | MTR**站点行程/票价表**、Citybus/KMB线路时刻/站序、运输署小巴页、实际渡轮时刻，步行两端另查。 | 实际线路/方向/分段费，区分公众与租户专车；路线经过数码港不证明所选方向可从家附近上车。 |
| 日本 | [Yahoo!路線情報](https://transit.yahoo.co.jp/)可读的实际到达日期/时刻查询结果；JR/私铁/地铁站点时刻与票价表，能读时使用NAVITIME/Jorudan。搜`"[駅A]" "[駅B]" 乗換 運賃`并打开结果。 | JR/Tokyo Metro/Osaka Metro及实际私铁路线/乘客票价，分IC/纸票/通勤券；站到站时间不含家门接驳。 |
| 德国 | 柏林/勃兰登堡跑`query_routes.py vbb`；其他地区DB/交通联合机构时刻或文档化获准API；慕尼黑MVV。 | VBB/MVV/DB正式票种、区域/列车等级覆盖；社区API或月票价格不独立证明门到门票价。 |
| 法国 | RATP/Île-de-France Mobilités或TCL线路PDF；已有配置时用获准Navitia/IDFM文档化API；Moovit/Rome2Rio参考线路＋接驳路网。 | 区域运营方当前票种、换乘、分区、订阅，不默认月票资格或雇主报销。 |
| 荷兰 | 9292/NS具体时刻、获准NS API；GVB/Hermes线路图/PDF＋接驳。搜`site:gvb.nl "[线路]" dienstregeling`或`site:hermes.nl "[站]" dienstregeling`。 | NS/GVB/Hermes实际路线/区域/里程/订阅；起步费不是完整票价。 |

第三方线路页也必须核其**实际起终点**、日期/服务范围以及总时长包括哪些段。Rome2Rio可能标题是城市/车站，但某选项从另一处发车；Moovit可能仅列附近站。其报价先当参考估计，回运营方确认。准确记录支持到哪对点/哪个时段，不能静默换起点。

如果铁路/公交未开放12月时刻，可以交付**明确标记的当前工作日参考行程**，不是未来承诺。月费据实际有来源的路线/乘客规则计算，付费备选与步行是不同情景。`check_commutes.py`只核输入的估计算术，状态不认证路线/来源可靠；须解释估计输入，不能改名为已核实。

## 买菜、药店与商圈

1. `pois`只查**小范围、有上限**OSM候选，或网页查商户官方门店定位器。Overpass失败时，可以对**从真实来源取得的一个具名商户/地址**用Photon解析，不全城扫商店；地理编码器不是完整商户目录。
2. 回零售商/商场官方locator核同一分店/地址：可选本地实际存在的Tesco/Sainsbury's/Boots、Whole Foods/CVS、Woolworths/Coles/Chemist Warehouse、New World/Countdown/Woolworths NZ、FairPrice/Cold Storage/Guardian、AEON/matsukiyo、REWE/dm/Apotheke、Carrefour/pharmacie、Albert Heijn/Etos/apotheek等，而非把全部品牌都跑完。搜`"[品牌/分店]" "[城市]" official store locator`；大陆/香港另查本地商场/店页及`超市/街市/药店`。
3. 查家门→分店的**步行路网**，报名称、类别/地址、路网距离/模型分钟、端点精度及链接。POI直线距离只排序，不能换算分钟。没有独立商户页则保留“地图候选＋模型路线”，不称营业已确认。
4. 营业时间、驻店药师、门店存在分别注明日期；OSM编辑时间不是最近营业核验。近邻标签不赋予处方、入学或诊疗资格。商圈说明实际功能，不数图标。

## 最少应交付什么

每个保留房源应有支持到一定范围的路线/标注估计、精确票价证据或条件票价情景，以及具名日常设施和各自到达证据。逐项分清：指定时刻行程、非时刻化步行模型、时刻表组合、第三方参考、发布者邻近宣传，不能互换。保存成功原始响应和失败；尝试有意义的独立替代后，剩余缺口仍可写明，但不能一个地图UI失败就放弃全部字段。

## 公开API政策与网页故障要分开

查询已文档化公开数据API时，同时读发布方API使用政策与该资源实际访问反馈。[Overpass手册](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html)明确支持额度内人工提交查询；通用API路径的索引禁令本身不等于禁止该文档允许的低量、用户指示调用。仅小范围查询、共享节流、缓存并署名；这不覆盖明确agent禁令、认证、验证码、核心403/429或已拒绝端点，也不能换host/身份规避。

Google[官方公开地图方向URL](https://developers.google.com/maps/documentation/urls/guide)为`https://www.google.com/maps/dir/?api=1&origin=...&destination=...&travelmode=transit`，不需要API key。先核当前精确路径政策及实际界面。URL本身不表达/证明所需定日行程，仍须设置支持的日期/到达选项并核返回各段/票价。本轮有限隔离浏览器尝试超时，所以只是可能的公众渠道，**不是已经验证的全球免key兜底**。普通传输超时后，可在如实身份不变的前提下做一次有时限HTTP兼容诊断；不启用隐身绕过、不关闭安全检查、不换身份，也不在访问拒绝后继续重试。
