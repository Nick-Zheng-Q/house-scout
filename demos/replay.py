#!/usr/bin/env python3
"""Offline replay of disclosed illustrative budgets against dated real-offer facts."""
import argparse
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('check_rentals',ROOT/'scripts/check_rentals.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def replay():
    inputs=json.loads((ROOT/'demos/inputs.json').read_text())
    rows=[module.summarize(x)['candidates'][0] for x in inputs]
    rent=inputs[2]['candidates'][0]['costs'][0]['amount'];deposit=inputs[2]['candidates'][0]['costs'][2]['amount']
    return {'scope':'Offline dated-facts replay, not current vacancy/live search/inspection or payment approval. Personas and budgets illustrative.', 'source_snapshot':'2026-10-20','cases':rows,
            'conditional_eindhoven_cash':{'assumption':'Only if first full rent and deposit both due at signing; timing unverified','subtotal':rent+deposit,'shortfall_vs_example_cash':rent+deposit-inputs[2]['budgets']['signing_cash_max'],'actual_due_unknown':True}}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();d=replay()
    if a.check:
        assert [x['hard_condition_gate'] for x in d['cases']]==['verify','reject','reject']
        assert d['cases'][0]['monthly_budget_status']=='unknown'
        assert d['cases'][1]['known_monthly']==110000 and d['cases'][1]['monthly_budget_status']=='over'
        assert d['cases'][2]['signing_cash_budget_status']=='unknown'
        assert d['conditional_eindhoven_cash']['subtotal']==4485 and d['conditional_eindhoven_cash']['shortfall_vs_example_cash']==485
    print(json.dumps(d,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
