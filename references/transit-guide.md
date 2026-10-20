# 实际时段的公共交通核查

需要或比较公交、地铁、有轨电车、铁路、渡轮时使用。先读[工具权限与服务政策](routing-guide.md)。**步行路线、价目表、附近站点、发车间隔或站间平均耗时，都不能验证公共交通通勤。** 步行只能单独比较；不能短途不方便坐车就换成步行、宣称公交条件已满足。

## 真正提交查询并保存返回证据

1. 保持原始起终点及精度，仅街道级房源仍是街道级。确认正确车站、方向和公众上车站；其他区同名站不能互换。只能取得站间资料就标注站间，不能把家搬到车站。
2. 向实际可用规划器/API提交**当地服务日期、到达/出发时刻、时区及公共交通方式**。配置了URL或打开空表单不算结果。保存参数、响应/来源URL、抓取UTC、实际返回日期时刻及全部段。到达查询须核最后到达确在目标当地日期且不迟于截止，不能只核请求含日期。
3. 保留每段线路/班次/trip、上下车站、返回的平台/方向、出发到达、换乘次数、换乘步行与等待、取消和运营提醒。单站发车板不能独立证明接续行程。核相邻段实际空间及时序连接；缺失换乘步行不能填0。
4. 查两端户外接驳；站内、站台转换另有依据或明确说明预留假设。步行路网只可提供**接驳组成部分**，不代替乘车或未查询的班次。接驳未核时仍可交付有用站间行程，但不称完整门到门。
5. 针对**已取得行程**查票价：成人/优惠、方式/运营方、具体分区/计费里程、支付方式、时段、生效日。优先返回路线价；否则逐实际段匹配官方票规，引用推导。通用月票价、用步行距离充计费公里、宣传起价、API的`null`都不是本次报价。目标日票价未发布时，当前有价参考与未来价格缺口分别保留。
6. 已知返程日期时刻则单独查询；否则只能列明确附条件的同覆盖返程费用情景，不能称反向已核。仅两向相关票价/换乘规则覆盖后按`次数×（去程价＋返程价）`算月费；月票另比资格及覆盖，不能相加。

## 补齐公众入口与换乘核查

先明确目的地精度再判定。用户只说火车站/MRT站时，应由运营方车站/出入口图或独立核实的入口地址，确定该站的**真实临街公众入口**，并写明使用哪一个入口；不要自动加上用户没要求的列车站台截止时间。反过来，附近公交站或地下地铁站台也不等于这个入口。若用户确实要赶某班火车，须另核到具体站台及提前上车余量。

保留原完整住址/楼宇入口与原目的车站和用途，不为凑通过改站。规划器若截断在地铁/公交站台，先核原铁路站公众入口，再以该入口地址/坐标查询整段行程，让规划器返回缺少的出站/接驳，并保留原站名查询对照。否则分别查实际下车点→已核入口、家门→实际上车点，结合车站布局/障碍核返回路径及吸附点。把地下站台坐标吸附到地面道路的步行模型，不包含楼梯、闸机或电梯。

进出地铁/铁路及换乘，优先采用规划器明确的出站/换乘段、官方GTFS `pathways.txt`实际通行时间、运营方最短接续说明，或由车站图支持路径、公开假设时长的站内模型。车站图本身证明布局，不证明测得分钟。若自行建模，应列路径距离、楼层/楼梯/电梯、速度假设与不确定性，标为模型而非运营方确认。随意填“入站3分钟/出站2分钟”没有证据基础。补全接驳后再核是否赶得上实际班次；必要时选更早班次，不能从喜欢的发车时间倒扣未知步行。

逐段记录起终点、时钟、来源类型（运营方规划器/时刻表/官方站图/独立步行模型）、距离、日期覆盖和不确定性。总时长从家门出发算到最终入口抵达；两段车之间的空档是**换乘时间间隔**，含步行时不能全算等待。步行、等待、站内通行应分开，不能把规划器已含接驳重复相加。只要所需连接无缺项、端点精度有依据，可以完成**计划/模型通勤核查**，但不等于现场测量或准点保证。没有依据的预留时间仍为缺口，不算已验证连接。

服务日期与价格证据日期分别记录。与实际线路、票区、支付和换乘匹配的返回/官方现行票价，可支持**按现价核算的定日计划**，须注明未来调价风险；未公布就不能保证未来固定票价。分别报告`dated_route_complete`、`entrance_connections_complete`、`transfer_connections_complete`、`current_itinerary_fare_matched`、`future_fare_confirmed`及整体范围。未来价格未知既不能编0，也不应抹去已经补齐路线与现价的计划。不同日期的完整参考仍不能算原日期完成。

## 超过时刻或售票范围

不得静默换日。先试用户日期，确实不可用后，再**另行提交一个精确日期的参考查询**，例如下一个适用工作日同一当地到达时刻，同时展示两个日期。当前有日期参考可支持估计，但不能通过原目标日要求。“每10分钟”是间隔，不是有日期班次；实时下一班不是明天08:30。

规划器因步行更短而不返回乘车时，记录实际响应。附近上车站可帮助查真实备选，但站间诊断或换终点是另一个范围，不能当原查询成功。解释是否实用，不为了增加通过数而制造无意义绕行。

## 规划器不可用时查官方GTFS

核运营方最新开发者/下载页和许可，将ZIP、来源URL、下载UTC、SHA256存于安装skill以外。地方feed够用就不批量下载整国。[GTFS规范](https://gtfs.org/documentation/schedule/reference/)定义服务日历、例外、站序、上下客与发车间隔模板；日期覆盖必须实际包含查询日。**还要核实发布者说明的导出日期和发布时限。若文件日历超出更短的官方发布时限，不能据此确认未来班次；即使脚本找到了有效 service ID，也只能记为未确认时刻记录。** 例如官方只承诺滚动30天数据，`calendar.txt`延伸至12月并不证明12月班次已发布。导出日期不明或说明冲突时，保留缺口，另取定日规划结果或已确认覆盖范围内的参考；下载时间不能重置基于导出的滚动时限。也要查具体线路的完整性说明；名义期限内的空结果仍不证明没有服务。本地脚本无法验证这个外部发布承诺。

`query_gtfs.py`是**直达站间时刻提取**，不是路由引擎；只读本地获准ZIP，不联网。先查看`stops.txt`独立匹配站ID/方向，父站仅展开真实子站；使用feed的`agency_timezone`与目标日期正确偏移：

```sh
python3 scripts/query_gtfs.py /path/to/authorized-feed.zip --from-stop ACTUAL_STOP_ID --to-stop ACTUAL_STOP_ID --arrival 2026-12-01T09:00:00-05:00 --timezone America/New_York --output /tmp/scheduled-trips.json
```

脚本核活动服务/日历例外、精确有序站时、上下客许可及前服务日24点以后时间；全部排除`frequencies.txt`模板和空时刻插值，不编精确发车。空结果不证明没有服务。发布方中途站估时（`timepoint=0`）保留估计标记，显示到秒也不是准点保证。保存选中原始站时行及feed哈希，但不返回票价、换乘方案或已核家门接驳。换乘须各段实际班次及有依据接驳/等待，不能加不接续的乘车分钟，也不能把列出的最晚直达班次说成全局最优路线。运营中断另查。

## 推荐和测试应分开的状态

分别报告：**原目标日公交行程、其他精确日期参考、仅站间、时刻表组成部分不完整、两端接驳、已匹配行程票价、条件价格情景**。完整原目标日公交验证要求在目标日期时段，有实际乘车且接续的行程、所声称精度下有依据的两端接驳及匹配票价。路线可得、端点精度、费用覆盖分字段保存，HTTP200或算术正确不能产生整体“通过”。


### 查铁路站公众入口的具体来源

德国用[DB车站页](https://www.bahnhof.de/)的Adresse及Lageplan/车站图，核街道门牌、入口/通道及施工日期。把已核临街入口作为MVV目的坐标后检查返回实际地址、楼层`niveau`和出站段：`niveau=-3`站区不是地面入口。保留阶梯/扶梯各层级和规划器总出站时长；总步行段含内置footpath时不能再加一次。多选更早行程留余量，不把09:00之后备选计入。

新西兰用AT/Metlink具体车站页的station map/access信息，而非仅公交站中心坐标。[AT](https://at.govt.nz/) Waitematā/Britomart页及其链接站图可核Tyler/Galway等公众入口和Commerce入口关闭说明；核说明适用日期，别沿用关闭入口。再查实际下车站→可用铁路入口的路网，保留绕行和吸附点，不能用直线几百米除速度代替实际路径。原址到上车点的地址/门点若仍有未核吸附差，报告范围，不冒充已测私宅门。

荷兰用[NS车站信息](https://www.ns.nl/stationsinformatie/)及市政/铁路运营方施工公告核公众入口，公众规划器可改查同一车站入口所在街道/门牌，但须核真实铁路入口而非附近办公楼。目标日期跨新通道开通/旧入口关闭时，当前地图不独立证明未来入口可用；例如Amsterdam Zuid的Brittenpassage/Minervapassage改造须核目标日布局。

## 可执行的规划器与时刻查询

以下联网命令仅用标准库HTTPS，与`query_routes.py`共用本机节流/缓存，保存请求URL、抓取UTC、原JSON和摘要。`--public-locations`仅确认公开测试或获准披露；坐标为**纬度,经度**，负数要用`--origin=-…,…`等号形式。 独立评估时在子命令之前给两个联网助手指定全新`--cache-dir /tmp/this-run-only-cache`；仍共享请求节流，但不读之前的原始响应缓存。

```sh
# 慕尼黑官网当前是/ng，不是已失效的/wwamd。
# 先核原楼宇与运营方确认的车站公众入口；填实际WGS84纬度,经度，不用站中心/旧示例点。
ORIGIN_WGS84="LATITUDE,LONGITUDE"
ENTRANCE_WGS84="LATITUDE,LONGITUDE"
python3 scripts/query_transit.py --public-locations --cache-dir /tmp/this-run-only-cache --output /tmp/mvv.json mvv --origin="$ORIGIN_WGS84" --destination="$ENTRANCE_WGS84" --arrival=2026-12-01T09:00:00+01:00
# 波士顿：同一trip在上下站的官方时刻，不拼两条互不相关的发车。
python3 scripts/query_transit.py --public-locations --output /tmp/mbta.json mbta --from-stop place-harsq --to-stop place-knncl --route Red --direction 0 --arrival=2026-12-01T09:00:00-05:00
```

MVV正常网页请求`/ng/XML_TRIP_REQUEST2`：`type_origin=coord`、`name_origin=经度:纬度:WGS84[DD.ddddd]`，终点同理；`itdDate=YYYYMMDD`、`itdTime=HHMM`、`itdTripDateTimeDepArr=arr`、`outputFormat=JSON`。适配器保留换乘footpath、返回票种和警告，独立标记迟到/错日方案；API可能同时返回一个合格和一个迟到方案。核实际解析的地址/入口。[MVV公众规划器](https://efa.mvv-muenchen.de/)网页接口会变化，不保证商业API稳定契约。

MBTA[官方V3规范](https://api-v3.mbta.com/docs/swagger/swagger.json)有`/stops`、`/schedules`、`/services`。先用`/stops?filter[route]=Red`核站ID、parent_station与方向；脚本查90分钟窗，同trip/站序/上下客匹配，保留`timepoint=false`发布估时，并暴露`links.next`不假装分页完整。选定trip后按其service关系查`/services/{id}`的起止日、valid_days、added_dates、removed_dates；另查`/alerts`的线路/车站/日期。它仍是**站间查询**，票价、家门/站台接驳另核。若地铁出入口路径无法建立，可比较真实直达地面公交：`/stops?filter[latitude]=LAT&filter[longitude]=LON&filter[radius]=0.005&filter[route_type]=3`查附近站；MBTA半径单位是**度，不是米**。用`/routes?filter[stop]=STOP_ID&filter[type]=3`查线路，核线路方向名与道路正确一侧的站，再对选中公交做同班次查询。用`/stops/{parent_id}?include=child_stops`及location type核真实公众入口，不把父站中心点当站门。这是实际替代方式，不是用步行代替公交；更早/更慢的方案须说明实用性。票价/CDN被封禁不能换镜像绕过。独立的第一方来源是MBTA自有[网站票价实现](https://github.com/mbta/dotcom/blob/main/lib/fares/fare_info.ex)，不是被拒网页的抓取镜像。核当前commit、成人`subway`/`single_trip`配置与支付方式；`lib/dotcom/trip_plan/fares.ex`核线路类型到票种映射，`lib/fares/repo.ex`核实际加载。留commit SHA/日期和代码行。这能支持现行官方票价，不是未来生效公告，也不证明站内通行时长。

## 按市场查精确的独立数据渠道

这些是具体操作，不承诺每个feed覆盖用户日期。下载前读发布方当前页面与许可；查feed_info、日历/例外、routes、trips、stop_times。有ZIP但routes空表或线路ID悬空，不等于可用规划器；不同feed的ID不能凭猜测拼合。

| 市场 | 去哪里、怎样取得真实时刻 | 票价与接驳边界 |
|---|---|---|
| 美国 | 波士顿用上方MBTA命令；SF打开[SFMTA GTFS](https://www.sfmta.com/reports/gtfs-transit-data)实际链接ZIP，先核日历再取Folsom/VanNess→4th&King的N班次；名为current也可能过期。 | 实际Muni/MBTA线路与官方支付票规；票价页打不开不代表0元。 |
| 英国 | TfL公众网页按**线路→正确方向车站→timetable**，不重试已403的API。剑桥[Whippet](https://www.whippetbus.co.uk/)→Universal U1/U2→有效日期PDF/正常公众时刻widget，核上车时间点、火车站站点及工作日/例外。 | TfL/Whippet本线路票种；站内接驳缺失仍是缺口。 |
| 加拿大 | [Toronto CKAN](https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show?id=merged-gtfs-ttc-routes-and-schedules)取resources当前ZIP，匹配实际地铁站台ID及有值的pathways.txt；温哥华[TransLink GTFS](https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources/gtfs/gtfs-data)当前静态文件或具体方向公交时刻。 | [TTC票价](https://cdn.ttc.ca/Fares-and-passes)、TransLink分区/支付；通路traversal_time缺失不能填0。 |
| 澳大利亚 | [Victoria目录](https://opendata.transport.vic.gov.au/)→GTFS→正确内嵌电车/铁路ZIP，按真实站与trip查；悉尼[Transport NSW](https://transportnsw.info/)→430等具体线路→有效日期及方向的**运营方PDF站时表**，或已有授权Open Data API。 | 免费电车区须实际上下站均满足；NSW班次另配Opal/支付规则及两端接驳。 |
| 新西兰 | [AT公开GTFS](https://gtfs.at.govt.nz/gtfs.zip)、[Metlink公开GTFS](https://static.opendata.metlink.org.nz/v1/gtfs/full.zip)，先回发布方开发页核实，按真实站ID跑query_gtfs.py；AT网页规划API需要subscription key，不能从应用抽取。 | AT官方City等分区图；Metlink真实站分区及高峰/非高峰；GTFS空zone需另源，不猜价格。 |
| 德国 | 柏林`query_routes.py vbb`明确到达偏移；慕尼黑上方/ng实际查询；其他城市另查本地数据，不扩张VBB覆盖。 | API空价与另源票规分开，保留MVV票种/区域/币种。 |
| 法国 | [data.gouv.fr数据集API](https://www.data.gouv.fr/api/1/datasets/?q=GTFS)→准确IDFM/GrandLyon发布方dataset→公开静态GTFS资源；官方规划API可能需已有IDFM/Navitia授权。 | 核日期范围及线路/票种区域；大文件超时不代表没有公交。 |
| 荷兰 | 优先正常[NS公众规划器](https://www.ns.nl/en/journeyplanner/)精确日期/Arrival及展开票价（下方步骤）；独立静态数据用[openOV](https://openov.nl/)→官方[GTFS目录](https://gtfs.ovapi.nl/)README/许可/识别UA→相应完整feed，优先有效地方数据；GOVI子集可能无routes表，不能编公众线路名或混ID。规划器受限则查GVB/Hermes具体方向时刻PDF。 | NS/GVB/Hermes实际路线/乘客票规；缺计费距离或产品仍未知扣费。 |
| 香港 | [运输署公开GTFS](https://static.data.gov.hk/td/pt-headway-en/gtfs.zip)按真实线路/方向/站ID查fare_rules、服务日历/发车间隔；KMB/Citybus实际方向时刻与运输署线表。 | HKeMobility公众UI实查仅星期＋出发钟点，不能冒完整日历日期/到达查询。中途站时刻空＋总站间隔不能外推精确上车钟点；具体上车分段票价仍可单独核实。 |
| 日本 | 先核独立[NAVITIME公众主站](https://www.navitime.co.jp/)政策与可见表单：`/route/comparison`查精确地址/POI定日出行、`/transfer/searchlist`查站间铁路，步骤见后文。京王车站/大阪Citybus官方时刻入口、有效日期平日PDF和IC/公交票规作第一方补查，核方向/生效日。Yahoo不能默认直连兜底：政策核查发现ChatGPT-User/GPTBot限制，不换UA绕过。仅解析用户提供或确实获准取得的保存页面；政策核查前200不证明可复用通道。 | 2025版PDF不独立证明2026年12月仍适用，站间不含地址接驳。 |
| 新加坡 | 已有获准[OneMap routing](https://www.onemap.gov.sg/apidocs/routing)/LTA：按当前文档提交pt、实际日期时刻/到达模式及获准配置Bearer token。匿名实际401后停止，不抽公众应用token。 | SimplyGo实际线路/里程/支付票规；请求已有授权，不编免key集成。 |
| 中国大陆 | robots允许的公众`https://www.amap.com/dir/`用URL编码的`from[name]`、`to[name]`、`type=bus`、`city`，核实际解析地点及返回线路/票价；可能只支持非时刻化线路参考，不是指定日期到达查询。文档化时刻API则用已有获准[高德公交路线API](https://lbs.amap.com/api/webservice/guide/api/direction)/百度同类；核城市代码、坐标系、文档日期/时刻字段及响应是否真正尊重时间。没有既有key就是认证API路径不可用，不代表所有公众路线页都不可用。 | 官方线路/分段/乘客票规；有路径耗时但无有日期发车依据不能算班次验证。 |

## 免费渠道不足时使用已有授权跨市场API

用户已有获准Google Routes项目且**明确允许计费调用**时，可按[官方公共交通API](https://developers.google.com/maps/documentation/routes/transit-route)向`https://routes.googleapis.com/directions/v2:computeRoutes`发POST；本skill不授权开户或开通计费。从获准配置在内存读key到`X-Goog-Api-Key`，不打印/保存该header。`Content-Type: application/json`；field mask用`routes.legs.steps,routes.duration,routes.travelAdvisory.transitFare,routes.localizedValues.transitFare`。示例body：

```json
{"origin":{"location":{"latLng":{"latitude":51.5266,"longitude":-0.0982}}},"destination":{"location":{"latLng":{"latitude":51.5257,"longitude":-0.0875}}},"travelMode":"TRANSIT","arrivalTime":"2026-12-01T09:00:00Z","computeAlternativeRoutes":true,"transitPreferences":{"routingPreference":"FEWER_TRANSFERS"}}
```

按目的地时区转换RFC3339，不盲套示例UTC。官方支持过去7天/未来100天，仍取决于当地数据/覆盖。核`steps[].transitDetails.stopDetails`上下车站/时刻、线路、全部步行换乘及末段接驳，请求含arrivalTime不等于已核。任何段票价未知时`travelAdvisory.transitFare`可能缺省，需查运营方，不填0。遵守服务保存/展示条款。本认证路径有文档但**本轮无凭证，未联网验收**。


## 工具列表没有交互浏览器时

先检查**已有且获准**的浏览器运行环境，不要直接断言不能交互。Codex本地桌面可用`load_workspace_dependencies`发现捆绑Node和包（含Playwright），再核`require('playwright')`及已安装Chromium可执行文件。不编MCP工具、不把开发者机器路径硬编码给用户、不自动安装包/浏览器、不打开用户已登录浏览器资料。

通过`exec_command`运行发现的Node及简短Playwright脚本：启动隔离浏览器/context，并将`timezoneId`设为目的地IANA时区（如`Australia/Sydney`、`Europe/Amsterdam`），如实标识agent（如`ChatGPT-User`），打开获准公众规划器，检查可见标签/输入框，填写**原始**起终点并选择实际自动补全项，设公共交通、明确日期及**到达前**而非出发，再提交。读取可见返回方案、展开换乘及票价，保存截图、可见正文、最终URL、操作和抓取UTC。须核实际返回钟点/时区而非只看表单：上海时区浏览器可能让悉尼09:00变12:00，即使URL看似正确。只保存空首页仅是能力发现。可作必要功能选项，不开户、购买或扩大权限；不读取内部key/token/cookie、不复制应用凭证替代身份验证。

核robots/网站政策，遇登录、CAPTCHA、明确封禁或限流就停；无stealth、代理、伪造身份或换客户端对抗封禁。某API端点被拒不自动证明独立公众UI也不可用，但不能重放被拒端点绕其限制。页面若仅有**星期＋出发时刻**就如实报告范围，不能表达具体日历日期到达查询。各运营方控件不同，应检查真实控件而非粘贴臆造selector；JS出现一个字段不证明表单支持它。

拒绝有具体资源范围：被拒字体/统计文件不重试，但它的失败不自动禁止其他正常获准路线表单。核心路由/认证请求或CAPTCHA被阻则停止该路径。浏览器ORB等安全错误不能通过关安全检查解决；核心脚本不能加载时记UI不可用，不编需要登录。


### 已实际可用的公众UI路线入口

**荷兰NS：**隔离`Europe/Amsterdam`context打开[NS Journeyplanner](https://www.ns.nl/en/journeyplanner/)，等真实cookie弹窗出现后拒可选追踪；起点选精确地址/门号自动补全项，终点选正确车站类型，不仅留一段输入文字。点可见**Arrival**标签（样式标签可能盖住radio），点可见日期按钮外层打开日历，选实际年月日、09:00，再点**Plan**，不是**Order train ticket**。核返回日期和行程钟点，展开方案及**More fares**完整票价；独立运营方规划器被限时，这里仍可能返回匹配旅程的GVB/Hermes价格，保留支付口径。终点若是铁路综合站内地铁站台，仍须核实际出口/铁路接驳，不能暗换目的地。核心请求被拒不绕；9292超时不阻止尝试独立NS公众规划器。

**悉尼：**独立[公众TripPlanner](https://transportnsw.info/trip-planner/plan)不同于已拒的旧XML端点。context设`Australia/Sydney`，用可见**Origin:**/**Destination:**选择真实建议，再**Selected time:**→**Arrive by**→**Day/Hour/Minute**→**Apply**。核实际日期选项；实见滚动未来14天，不是12月时刻。展开返回卡片：即使标题公共交通、启用多种方式，**仅步行**卡也不是公交。有效方向运营方PDF可支持单列较慢公交备选，但两端接驳和票价要匹配。

**英国剑桥：**[Whippet U1](https://www.whippetbus.co.uk/times/universal/u1/)/[U2](https://www.whippetbus.co.uk/times/universal/u2/)跟当前运营方公开时刻widget链接，保留公众嵌入标识，匹配`serviceName`/`ticketerCode`并按公开参数设`date=YYYY-MM-DD`，核返回selectedDate及同一列上下站时刻。当前公开路径`portal.whippetbus.co.uk/v4/widget/embeded/timetable`不是API密钥；重新从官网发现链接，不编标识。宽泛endDate不证明所有服务日均确认；WAF/challenge202虽2xx也必须停，不解挑战或换身份。保留PDF生效日和站名差异。


### 日本：NAVITIME公众定日查询与车站入口步行

获准的主域名`www.navitime.co.jp`与被拒的`transfer-train.navitime.biz`、受限Yahoo页面是独立公众服务；使用前核具体域名/路径现行政策。别处被拒既不允许重试那个资源，也不证明这个独立站不可用。只用正常公众表单，不登录、开会员或提取应用凭证。

直接从普通公众比较搜索开始：`https://www.navitime.co.jp/route/comparison?orvName=URL编码的完整地址&dnvName=URL编码的车站名`，`orvName`、`dnvName`是本次实际公众检索字段。首页可能转到另一个本环境不可用的核心页面`/maps/routeSearch`，可以走独立比较表单，不是重试失败的产品。在可见建议中找精确楼宇/地址和车站，核完整名称、都道府县、类型及运营方：泛称车站可能落到附近**JR**站而非用户要去的**Osaka Metro**站。保留原目的地及选中ID。公众`/route/comparison`使用表单实际`orvSpotCode`、`dnvSpotCode`、`date=YYYY-MM-DD`、`hour`、`minute`、`basis`（本次可见`0`为到达）；以当时实际控件及返回日期/时钟为准，不保证参数永不改变。`/transfer/searchlist`有自己的站ID和表单字段，不能拿猜测的POI ID拼接。站间查询成功不代表需要登录的总导航页面可用。

展开公交/铁路备选，保留上/下车点、运营方/线路、方向、定日发到时刻、步行、换乘及路线票价/支付。纯步行或道路驾车结果不算公交。终点临街入口先用运营方官方站图（如Osaka Metro站点指南→当前构内图）核编号公众出入口，再在NAVITIME搜同一编号入口，跟正常**步行路线**链接`/walk/route/guidance/...`，保存实际ID、距离、转向和显示时间。此步行只补定日乘车的接驳，不取代公交/铁路；站POI或列车站台图标不证明已到该临街入口。组合时不重复加规划器已含步行，选能接上的更早班次，并把加的候车余量标为计划而非实测等待。



### 新加坡：独立获准的公众参考渠道

核[GoThere](https://gothere.sg/)具体路径政策。公众`/m/directions`有`from`、`to`及明确`mode=t`（公交/铁路）或`mode=b`（仅公交），参数来自实际方式切换链接。不填方式可能返回驾车，须看实际模式。OneMap无授权时，它可补具名上下车点、站出口、接驳距离及票价。本次公众表单**没有日历日期/到达时刻控件**，不能编date参数或把约等几分钟变成未来发车；只算未定日路线参考，不算指定日期通勤完成。robots禁止的`/-/`服务不能当替代API调用。短途不返回乘车不等于全城没有公交。

NS日历交互须读当时可见DOM，等待显示月份真正变化后，再点实际日期单元格；仅按role选控件可能不适配自定义日历。用实际可见aria-label/日期，不把当次CSS类硬编码为永久接口；规划后再核返回日期和到达模式。

## 本轮剩余城市排查补充

**完整规划器的接驳段：**定日完整地址→已核实公众入口**街面口**的结果，可以提供本身的首末步行。保留完整返回步行，不用更短的泛称站点质心路线替代。用运营方场站图核实际到达站台/站杆及公共步道连接；两个站台都通向同一公共步道时，不必凭空增加站内换乘。路径已有依据时不强制第二个步行模型重复证明；真实楼层、关闭/私人通道或站台冲突仍要补齐。地铁编号口应明确街面口还是楼梯底，不自行增加站台到达要求。

**日本地面公交：**NAVITIME公众公交表单为`/bustransit/search`，用实际可见`orvStationCode`、`dnvStationCode`；从选中的站点链接发现编码，不猜铁路ID或套旧参数。设表单日期/到达模式并核返回时钟，展开实际下车站台/站杆。东急/Citybus成人IC、现金价去运营方票规核。大阪以Citybus大阪駅前场站图与Osaka Metro梅田出口图共同核验：泛称公交站质心可能比实际到达站台更靠近8号口。通过完整地址比较表单搜精确入口POI，保留全程末段步行；入口POI编码不按出口编号连续递增。

**波士顿门口来源：**[剑桥市GIS官方仓库](https://github.com/cambridgegis/cambridgegis_data)提供AddressPoints、建筑轮廓、人行道和私人步道。精确搜门牌/街道，检查`Entry`、建筑ID、几何和图层元数据；地址点不自动等于门口。先沿有依据的院落/公共前庭路径接到人行道，再用步行路由，不直线跨花园/建筑消除吸附偏差。列出短接驳模型、非零地图误差及私人前庭通行假设。这是地图支持的公共地址精度，不是私人房门实测。使用实际公交站和MBTA对应公交票种，不能用地铁价算68路。

**柏林地面备选：**地铁站内连接难以核实时，可用`query_routes.py vbb`比较原地址真实纯公交方案。保留每段站ID、方向和坐标，按精确换乘站名查[BVG官方站区图](https://www.bvg.de/)，对照行程几何核实际下车杆、下一段上车杆。同名不等于同杆；4分钟间隔也要分步行、过街和等待。最终铁路入口查[DB Hauptbahnhof站点资料](https://www.bahnhof.de/)。接驳、换乘、到达时限及AB/BC/ABC票价匹配后才是完整公交备选。

**阿姆斯特丹施工：**从当前[Brittenpassage项目](https://zuidas.nl/en/construction-project/brittenpassage/)及市政[2026年11月站南侧调整](https://zuidas.nl/en/blog/2026/08/13/changes-to-station-area-near-gustav-mahlerlaan/)进入适用日期的行人地图。展开NS末段步行指引，把实际坐标与目标日布局核对。12月查询仍可能返回旧站台步行几何；日期正确、终点落在Arnold Schönberglaan街道都不独立证明已到新铁路门口。布局未能核清则保留定日乘车的部分结果，或查到同一入口的真实地面备选。

**多伦多服务条款：**TTC公众规划器可能嵌入Transit app。iframe能打开不等于允许自动化：[Transit条款](https://transitapp.com/terms)第4(v)节限制自动bot/scraper，不因TTC嵌入就自动操作该产品。改用获准TTC开放数据/运营资料、已有独立授权路由或用户提供结果；保留日期覆盖及站内接驳缺口。

**新加坡已有授权：**[OneMap官方agent MCP](https://www.onemap.gov.sg/apidocs/mcp)的`routing___transport`支持WGS84起终点、`routeType=pt`、mode、`MM-DD-YYYY`日期、`HH:MM:SS`时刻、`maxWalkDistance`和`numItineraries`。需要已有注册账号/token，发现文档不授权注册。除非当前文档/返回结果明确支持到达模式，time按出发处理，查可行的更早出发并核最终到达。没有可用token即本轮该路径不可用，不能称已验收；GoThere仍只是无日期参考。
