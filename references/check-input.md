# 租赁费用与硬条件检查脚本输入

运行 `python3 scripts/check_rentals.py path/to/input.json --pretty`。脚本只做算术和状态汇总；不验证房源、来源、授权或费用是否完整。所有金额用同一货币；月费按预计用量折算为月度。

```json
{
  "currency": "CNY",
  "hard_requirements": ["允许养猫", "十月入住"],
  "budgets": {"monthly_max": 6000, "upfront_plus_deposit_max": 12000, "signing_cash_max": 18000},
  "candidates": [{
    "id": "listing-123",
    "required_costs_complete": false,
    "signing_costs_complete": false,
    "conditions": {"允许养猫": "unknown", "十月入住": "met"},
    "costs": [
      {"name": "月租", "kind": "recurring", "amount": 5000, "signing_amount": 10000},
      {"name": "水电", "kind": "recurring", "amount": null, "signing_amount": 0},
      {"name": "中介费", "kind": "upfront", "amount": 2500, "signing_amount": 2500},
      {"name": "押金", "kind": "deposit", "amount": 5000, "signing_amount": 5000}
    ]
  }]
}
```

`kind` 为 `recurring`（月度）、`upfront`（前期不可退）或 `deposit`（可退押金）。`amount` 是非负单价，未知用 `null`；`quantity` 默认 1。`required:false` 不计入基础费用；优惠不要写成负数，另列条件情景。缺失的硬条件按 `unknown` 处理；状态只能为 `met`、`unmet`、`unknown`、`conflict`。有 `unmet` 为 `reject`，有未知或冲突为 `verify`，全满足才是 `pass`。

`required_costs_complete` 默认 `false`，只有证据显示必要收费范围已核全才设为 `true`。三类费用各需一条必需项；确认没有时显式填金额 0。超预算的已知小计可直接判 `over`；低于预算但仍有未知或范围未核全，判 `unknown`。

`signing_amount` 是该项目在签约时**实际需支付的总额**，不是每月单价乘以 `quantity`；例如月租 5000、签约预付两月就填 10000，已确认签约时不付的项目显式填 0。未确认填 `null` 或省略。`signing_costs_complete` 仅在签约时所有必需收费及其付款节点均有依据时设为 `true`；未列出项目不能靠此标志变成零。`signing_cash_max` 用它单独比较，输出仍须列明逐项依据。`upfront_plus_deposit_max` 不含预付租金，**不是签约现金需求**。脚本不适用于购房。


书面比较与脚本`conditions`必须使用相同的有依据硬条件状态。当前报价已明确违反硬条件时，不能以“保守”为由留空或改成未知；未来可能协商的条件另列情景，不抹去当前不满足。

`known_refundable_deposit`仅是脚本押金分类合计，不是保证可全退。已披露固定扣款、敷引/償却或条件扣除时，另列应付押金、已知扣除及可退部分是否确定；脚本不建模扣除，不能把押金原额当作确定回收额。
