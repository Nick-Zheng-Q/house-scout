#!/usr/bin/env python3
"""Build/verify a small reproducible skill archive; never publish or run networking."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_STEMS = (
    'candidate-record', 'check-input', 'commute-input', 'enrichment-guide',
    'platforms', 'purchase-guide', 'recommendation-guide', 'rental-guide',
    'search-guide', 'international-markets', 'cost-comparison', 'routing-guide',
    'transit-guide', 'validation-status',
)
HELPERS = ('check_rentals', 'check_commutes', 'normalize_costs', 'query_routes',
           'query_gtfs', 'query_transit')
MANIFEST = 'release-manifest.json'


def sources(root=ROOT):
    files = {n: root / n for n in ('SKILL.md', 'SKILL.en.md', 'LICENSE', 'install.sh', 'update.sh')}
    files.update({'README.md': root / 'RELEASE.md', 'README.en.md': root / 'RELEASE.en.md'})
    for stem in REFERENCE_STEMS:
        for suffix in ('.md', '.en.md'):
            name = f'references/{stem}{suffix}'
            files[name] = root / name
    files.update({f'scripts/{n}.py': root / f'scripts/{n}.py' for n in HELPERS})
    return files


def build(output, label, root=ROOT):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,47}', label):
        raise ValueError('label must be 1..48 ASCII letters/digits/dots/underscores/hyphens, starting with a letter/digit')
    files = sources(root)
    contents = {}
    for name, path in files.items():
        if path.is_symlink() or not path.is_file() or any((root / p).is_symlink() for p in path.relative_to(root).parents if p != Path('.')):
            # Check resolved containment too: never package a source from outside the checkout.
            raise ValueError(f'missing or symlinked release source: {name}')
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f'source escapes checkout: {name}')
        contents[name] = path.read_bytes()
        if len(contents[name]) > 2_000_000:
            raise ValueError(f'release source too large: {name}')
    manifest = {'schema_version': 1, 'name': 'house-scout', 'label': label,
                'status': 'preview_candidate_not_published',
                'files': {n: {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
                          for n, b in sorted(contents.items())}}
    contents[MANIFEST] = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    output = Path(output)
    if output.exists():
        raise ValueError('output already exists; choose a new filename')
    if not output.name.endswith('.tar.gz'):
        raise ValueError('archive output must end in .tar.gz')
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = io.BytesIO()
    with gzip.GzipFile(fileobj=payload, mode='wb', filename='', mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.USTAR_FORMAT) as tar:
            for name, body in sorted(contents.items()):
                info = tarfile.TarInfo('house-scout/' + name)
                info.size = len(body)
                info.mode = 0o755 if name.endswith('.sh') else 0o644
                info.mtime = 0
                info.uid = info.gid = 0
                info.uname = info.gname = ''
                tar.addfile(info, io.BytesIO(body))
    with output.open('xb') as stream:
        stream.write(payload.getvalue())
    return verify(output)


def verify(archive):
    # Read only, without extraction or execution. The allowlist is deliberate.
    allowed = {'house-scout/' + n for n in sources()}
    allowed.add('house-scout/' + MANIFEST)
    contents = {}
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            path = PurePosixPath(member.name)
            if (not member.isfile() or member.name not in allowed or
                    '..' in path.parts or path.is_absolute() or member.name in contents or
                    member.size > 2_000_000):
                raise ValueError(f'unsafe/unexpected archive member: {member.name}')
            contents[member.name] = tar.extractfile(member).read()
    if set(contents) != allowed:
        raise ValueError('archive is missing required runtime/documentation files')
    manifest = json.loads(contents['house-scout/' + MANIFEST])
    if not isinstance(manifest, dict):
        raise ValueError('release manifest must be an object')
    if (manifest.get('schema_version') != 1 or manifest.get('name') != 'house-scout' or
            manifest.get('status') != 'preview_candidate_not_published' or
            not isinstance(manifest.get('label'), str) or
            not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,47}', manifest['label'])):
        raise ValueError('unexpected release manifest')
    expected_names = {n.removeprefix('house-scout/') for n in allowed} - {MANIFEST}
    if not isinstance(manifest.get('files'), dict) or set(manifest['files']) != expected_names:
        raise ValueError('manifest file list differs from archive allowlist')
    for name, record in manifest['files'].items():
        if (not isinstance(record, dict) or type(record.get('bytes')) is not int or
                record['bytes'] < 0 or not isinstance(record.get('sha256'), str) or
                not re.fullmatch(r'[a-f0-9]{64}', record['sha256'])):
            raise ValueError(f'invalid manifest record: {name}')
        body = contents['house-scout/' + name]
        if len(body) != record['bytes'] or hashlib.sha256(body).hexdigest() != record['sha256']:
            raise ValueError(f'checksum mismatch: {name}')
    return {'ok': True, 'name': 'house-scout', 'label': manifest['label'],
            'files': len(contents), 'bytes': Path(archive).stat().st_size,
            'sha256': hashlib.sha256(Path(archive).read_bytes()).hexdigest(),
            'published': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--output', type=Path)
    group.add_argument('--verify', type=Path)
    p.add_argument('--label', default='preview')
    a = p.parse_args()
    try:
        result = verify(a.verify) if a.verify else build(a.output, a.label)
    except (ValueError, OSError, KeyError, TypeError, tarfile.TarError) as e:
        p.exit(2, f'{e}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
