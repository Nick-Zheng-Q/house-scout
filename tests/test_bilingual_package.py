import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = [
    "candidate-record", "check-input", "commute-input", "enrichment-guide",
    "platforms", "purchase-guide", "recommendation-guide", "rental-guide",
    "search-guide", "international-markets", "cost-comparison", "routing-guide", "transit-guide", "validation-status",
]


class BilingualPackageTests(unittest.TestCase):
    def test_both_skill_versions_and_reference_pairs_exist(self):
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "SKILL.en.md").is_file())
        for name in REFERENCES:
            with self.subTest(name=name):
                self.assertTrue((ROOT / "references" / f"{name}.md").is_file())
                self.assertTrue((ROOT / "references" / f"{name}.en.md").is_file())

    def test_local_markdown_links_resolve(self):
        files = [ROOT / "SKILL.md", ROOT / "SKILL.en.md", ROOT / "README.md", ROOT / "README.en.md"]
        files.extend((ROOT / "references").glob("*.md"))
        for path in files:
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in target and not target.startswith("#"):
                    with self.subTest(path=path.name, target=target):
                        self.assertTrue((path.parent / target).exists())


if __name__ == "__main__":
    unittest.main()
