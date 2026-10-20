import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import package_v100 as pkg

class V100Packages(unittest.TestCase):
    def test_reproducible_and_private_files_excluded(self):
        with tempfile.TemporaryDirectory() as t:
            a=pkg.build(Path(t)/'a');b=pkg.build(Path(t)/'b')
            self.assertEqual(a,b)
            self.assertTrue(all('.release-private' not in n and not n.startswith('tests/results/') for n in a['files']))
            for n in a['artifacts']:
                self.assertEqual((Path(t)/'a'/n).read_bytes(),(Path(t)/'b'/n).read_bytes())
    def test_runtime_copies_identical_and_bilingual(self):
        files,runtime,plugin=pkg.public_files()
        for n,b in runtime.items():
            self.assertEqual(files['skills/house-scout/'+n],b)
            self.assertEqual(plugin['skills/house-scout/'+n],b)
        self.assertIn('SKILL.en.md',runtime)
    def test_openai_local_execution_and_no_mcp_hooks(self):
        _,_,plugin=pkg.public_files();m=json.loads(plugin['plugin.json'])
        self.assertTrue(m['extensions']['com.openai']['requires_local_executor'])
        self.assertFalse(any('mcp' in n.lower() or 'hook' in n.lower() for n in plugin))
        self.assertNotIn('onboardingSkill',m['extensions']['com.openai'])
    def test_marketplace_relative_paths_exist(self):
        files,_,_=pkg.public_files()
        for n in ('.claude-plugin/marketplace.json','.agents/plugins/marketplace.json'):
            d=json.loads(files[n]);source=d['plugins'][0]['source'];path=source if isinstance(source,str) else source['path']
            self.assertIn(path.removeprefix('./')+'/skills/house-scout/SKILL.md',files)
    def test_archives_platform_overlays_do_not_conflict(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'build';pkg.build(p)
            with zipfile.ZipFile(p/'house-scout-openai-v1.0.0.zip') as z:
                self.assertIn('plugin.json',z.namelist());self.assertFalse(any(n.startswith(('.claude-plugin/','.codex-plugin/')) for n in z.namelist()))
            with zipfile.ZipFile(p/'house-scout-claude-v1.0.0.zip') as z:
                self.assertIn('.claude-plugin/plugin.json',z.namelist());self.assertNotIn('plugin.json',z.namelist())
    def test_demo_actual_unknown_signing_not_replaced_by_scenario(self):
        spec=importlib.util.spec_from_file_location('demo_replay',ROOT/'demos/replay.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);d=m.replay()
        self.assertEqual([x['hard_condition_gate'] for x in d['cases']],['verify','reject','reject'])
        self.assertEqual(d['cases'][2]['signing_cash_budget_status'],'unknown')
        self.assertEqual(d['conditional_eindhoven_cash']['shortfall_vs_example_cash'],485)
    def test_existing_output_not_overwritten(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'build';pkg.build(p)
            with self.assertRaisesRegex(ValueError,'new directory'):pkg.build(p)

if __name__=='__main__':unittest.main()
