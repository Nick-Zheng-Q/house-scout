import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('build_release', ROOT / 'scripts/build_release.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / 'source'
        for name, source in m.sources().items():
            rel = source.relative_to(ROOT)
            out = self.root / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, out)

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, name='candidate.tar.gz'):
        p = self.base / name
        m.build(p, 'preview-test', self.root)
        return p

    def test_reproducible_allowlist_and_sensitive_or_test_files_excluded(self):
        (self.root / 'tests').mkdir()
        (self.root / 'tests/private-response.json').write_text('not for distribution')
        (self.root / 'references/private-notes.txt').write_text('not for distribution')
        a = self.build()
        b = self.build('second.tar.gz')
        self.assertEqual(a.read_bytes(), b.read_bytes())
        result = m.verify(a)
        self.assertTrue(result['ok'])
        self.assertFalse(result['published'])
        with tarfile.open(a, 'r:gz') as t:
            names = t.getnames()
            self.assertEqual(set(names), {'house-scout/' + x for x in m.sources()} | {'house-scout/release-manifest.json'})
            self.assertFalse(any('tests/' in x or 'private' in x or '__pycache__' in x for x in names))
            self.assertIn(b'Required Notice:', t.extractfile('house-scout/LICENSE').read())

    def test_distributed_markdown_links_resolve(self):
        a = self.build()
        with tarfile.open(a, 'r:gz') as t:
            names = set(t.getnames())
            for member in t.getmembers():
                if not member.name.endswith('.md'):
                    continue
                for link in re.findall(r'\]\(([^)]+)\)', t.extractfile(member).read().decode()):
                    if '://' in link or link.startswith('#'):
                        continue
                    target = str(Path(member.name).parent / link.split('#')[0])
                    self.assertIn(target, names, (member.name, link))

    def test_archive_clean_install_update_and_all_helpers_work_offline(self):
        a = self.build()
        unpack = self.base / 'unpack'
        with tarfile.open(a, 'r:gz') as t:
            # verify() already checked the exact regular-file allowlist.
            m.verify(a)
            for member in t.getmembers():
                target = unpack / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(t.extractfile(member).read())
                target.chmod(0o755 if member.name.endswith('.sh') else 0o644)
        source = unpack / 'house-scout'
        dest = self.base / 'skills'
        subprocess.run(['sh', str(source / 'install.sh'), '--dest-dir', str(dest)], check=True, capture_output=True)
        subprocess.run(['sh', str(source / 'update.sh'), '--dest-dir', str(dest)], check=True, capture_output=True)
        installed = dest / 'house-scout'
        for helper in m.HELPERS:
            subprocess.run(['python3', str(installed / 'scripts' / (helper + '.py')), '--help'], check=True, capture_output=True)
        self.assertTrue((installed / 'references/validation-status.en.md').is_file())
        self.assertFalse((installed / 'tests').exists())

    def test_missing_file_fails_before_writing_archive(self):
        (self.root / 'LICENSE').unlink()
        p = self.base / 'candidate.tar.gz'
        with self.assertRaises(ValueError):
            m.build(p, 'preview', self.root)
        self.assertFalse(p.exists())

    def test_symlinked_file_and_parent_are_not_packaged(self):
        secret = self.base / 'outside'
        secret.write_text('outside')
        path = self.root / 'LICENSE'
        path.unlink()
        path.symlink_to(secret)
        with self.assertRaises(ValueError):
            self.build()
        path.unlink()
        shutil.copy2(ROOT / 'LICENSE', path)
        shutil.move(self.root / 'references', self.base / 'refs')
        (self.root / 'references').symlink_to(self.base / 'refs', target_is_directory=True)
        with self.assertRaises(ValueError):
            self.build()

    def test_invalid_label_and_overwrite_refused(self):
        for label in ['../release', '', 'with space', 'x' * 49]:
            with self.assertRaises(ValueError):
                m.build(self.base / 'candidate.tar.gz', label, self.root)
        a = self.build()
        digest = hashlib.sha256(a.read_bytes()).hexdigest()
        with self.assertRaises(ValueError):
            m.build(a, 'preview', self.root)
        self.assertEqual(hashlib.sha256(a.read_bytes()).hexdigest(), digest)

    def test_tampered_file_is_rejected(self):
        a = self.build()
        bad = self.base / 'tampered.tar.gz'
        with tarfile.open(a, 'r:gz') as src, tarfile.open(bad, 'w:gz') as dst:
            for member in src:
                body = src.extractfile(member).read()
                if member.name == 'house-scout/LICENSE':
                    body += b'changed'
                member.size = len(body)
                dst.addfile(member, io.BytesIO(body))
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            m.verify(bad)
        # A checksum manifest with the wrong JSON shape is rejected explicitly.
        malformed = self.base / 'malformed-manifest.tar.gz'
        with tarfile.open(a, 'r:gz') as src, tarfile.open(malformed, 'w:gz') as dst:
            for member in src:
                body = src.extractfile(member).read()
                if member.name == 'house-scout/release-manifest.json':
                    body = b'[]'
                member.size = len(body)
                dst.addfile(member, io.BytesIO(body))
        with self.assertRaisesRegex(ValueError, 'manifest must be an object'):
            m.verify(malformed)

    def test_unexpected_or_traversal_member_is_rejected_without_extraction(self):
        bad = self.base / 'unsafe.tar.gz'
        for name in ['house-scout/../outside', 'house-scout/private.json']:
            with tarfile.open(bad, 'w:gz') as tar:
                item = tarfile.TarInfo(name)
                item.size = 1
                tar.addfile(item, io.BytesIO(b'x'))
            with self.assertRaisesRegex(ValueError, 'unsafe/unexpected'):
                m.verify(bad)


if __name__ == '__main__':
    unittest.main()
