# 出行费用核算输入

`python3 scripts/check_commutes.py input.json --pretty` 只核算已经查询并录入的路线；**不会调用地图、推断票价或选择最快路线**。从具体房源出入口到用户目的地查询，记录工作日/周末、到达或出发时段、地图/交通来源及查询日。每个候选对每个目的地录入一种计划实际使用的方式；其他备选方式在候选记录另列，不叠加计算。

```json
{
  "currency": "CNY",
  "transport_monthly_max": 500,
  "destinations": [
    {"id": "office-a", "visits_per_month": 20},
    {"id": "office-b", "visits_per_month": 12}
  ],
  "candidates": [{
    "id": "north-unit-805",
    "routes": [
      {"destination": "office-a", "mode": "metro", "outbound_minutes": 47,
       "return_minutes": null, "outbound_cost": 5, "return_cost": null,
       "extra_monthly_cost": 0, "cost_scope_confirmed": false},
      {"destination": "office-b", "mode": "bus", "outbound_minutes": 38,
       "return_minutes": null, "outbound_cost": 3, "return_cost": null,
       "extra_monthly_cost": 0, "cost_scope_confirmed": false}
    ]
  }]
}
```

每条路线的月费用 = `visits_per_month × (outbound_cost + return_cost) + extra_monthly_cost`。示例只有去程票价，已知小计为 `20×5+12×3=136` 元/月，完整月费未知。**另行确认返程票价分别为 5 和 3 元且必要费用范围完整后**，往返情景才是 `20×(5+5)+12×(3+3)=272` 元/月。金额和时间是非负数；未知填 `null` 或省略，**确认没有额外月费时填 0**。`cost_scope_confirmed` 只在已核清该方式的必要票价、换乘、停车、过路费、能源费或通行证等适用项目时为 `true`；对打车动态报价，通常只能给查询时估价，不能保证未来月费。已知小计超预算可判 `over`；否则缺路线、任一费用未知或范围未核清均为 `unknown`。

单程与返程可能采用不同路线或票价，不默认相同。只查到早高峰时可单独展示早高峰门到门时间，但返程时间应标未知；脚本不把单程时间乘二。实际行程可能因班次、拥堵和天气变化，核算结果是**按输入假设的估计**，不是准点保证。

住房月费与交通月费合并时，先确认用户预算是否包含通勤。只合并两边同币种、同月度、同居住人数和实际出行次数的**已知必要项目**；任一边有未知必要费用时，结果仍是已知小计而非总成本。购房月供、物业和交通也可列为月现金流情景，但税费、首付和贷款资格不能由本脚本核算。
