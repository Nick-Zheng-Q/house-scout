#!/usr/bin/env python3
"""Prepare deterministic v1.0.0 source/skill/plugin/media packages. No networking or publication."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile
import build_release as base

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.0.0'
URL = 'https://github.com/Nick-Zheng-Q/house-scout'
PUBLIC_ROOTS = ('SKILL.md','SKILL.en.md','LICENSE','VERSION','README.md','README.en.md',
                'RELEASE.md','RELEASE.en.md','PRIVACY.md','THIRD_PARTY.md','install.sh','update.sh')


def encoded(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()


def checked(path, root):
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('missing, symlinked or escaping source: '+str(path.relative_to(root)))
    if any((root/p).is_symlink() for p in path.relative_to(root).parents if p != Path('.')):
        raise ValueError('symlinked source directory')
    b=path.read_bytes()
    if len(b)>2_000_000:raise ValueError('public source too large: '+path.name)
    return b


def public_files(root=ROOT):
    if (root/'VERSION').read_text().strip()!=VERSION:raise ValueError('unexpected VERSION')
    meta=json.loads((root/'release/v1.0.0/listing.json').read_text())
    if meta['version']!=VERSION or meta['name']!='house-scout':raise ValueError('listing/version mismatch')
    files={n:checked(root/n,root) for n in PUBLIC_ROOTS}
    for directory,patterns in [('references',('*.md',)),('scripts',('*.py',)),
            ('tests',('test_*.py','test_install.sh')),('docs',('*.md',)),
            ('demos',('*.json','*.py','*.md')),('release/v1.0.0',('listing.json','RELEASE_NOTES.md','verification.json')),
            ('release/v1.0.0/assets',('*.svg','*.html','*.png'))]:
        for pattern in patterns:
            for p in sorted((root/directory).glob(pattern)):
                files[p.relative_to(root).as_posix()]=checked(p,root)
    files['.gitignore']=b'__pycache__/\n*.py[cod]\n.DS_Store\ndist/\n.release-private/\ntests/results/\n.env\n.env.*\n'
    runtime={n:checked(p,root) for n,p in base.sources(root).items()}
    for n in ('VERSION','PRIVACY.md','THIRD_PARTY.md'):runtime[n]=files[n]
    # Dedicated clean directory for Skills CLI. Root source remains testable independently.
    files.update({'skills/house-scout/'+n:b for n,b in runtime.items()})
    common={'name':'house-scout','version':VERSION,'description':meta['description'],
            'author':{'name':'Dayweaver','url':'https://dayweaver.site/'},
            'homepage':URL,'repository':URL,'license':'PolyForm-Shield-1.0.0','keywords':meta['keywords']}
    interface={'displayName':'House Scout','shortDescription':meta['short_description'],
               'longDescription':meta['description']+' '+meta['benchmark_disclosure'],
               'developerName':'Dayweaver','category':'Productivity',
               'capabilities':['Compare housing evidence'], 'defaultPrompt':[meta['default_prompt']],
               'logo':'./assets/icon.svg','composerIcon':'./assets/icon.svg',
               'websiteURL':URL,'supportURL':URL+'/issues'}
    plugin={'skills/house-scout/'+n:b for n,b in runtime.items()}
    plugin.update({'plugin.json':encoded({'$schema':'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',**common,
                   'extensions':{'com.openai':{'interface':interface,'requires_local_executor':True}}}),
                   '.codex-plugin/plugin.json':encoded({**common,'skills':'./skills/','interface':interface,'requires_local_executor':True}),
                   '.claude-plugin/plugin.json':encoded(common),
                   'LICENSE':files['LICENSE'],'PRIVACY.md':files['PRIVACY.md'],'THIRD_PARTY.md':files['THIRD_PARTY.md'],
                   'README.md':b'# House Scout v1.0.0\n\nA Dayweaver housing-research skill. Requires host-authorized browsing/maps and Python3.9+ for local helpers. No MCP server, hooks, telemetry, or automatic transactions. See skills/house-scout/references/validation-status.en.md.\n',
                   'assets/icon.svg':files['release/v1.0.0/assets/icon.svg']})
    files.update({'plugins/house-scout/'+n:b for n,b in plugin.items()})
    files['.claude-plugin/marketplace.json']=encoded({'name':'house-scout-marketplace','owner':{'name':'Dayweaver'},
        'description':'Evidence-based housing research by Dayweaver','plugins':[{'name':'house-scout','source':'./plugins/house-scout','description':meta['description']}]})
    files['.agents/plugins/marketplace.json']=encoded({'name':'house-scout-marketplace','interface':{'displayName':'House Scout'},
        'plugins':[{'name':'house-scout','source':{'source':'local','path':'./plugins/house-scout'},'category':'Productivity'}]})
    return files,runtime,plugin


def zip_bytes(path, files):
    with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in sorted(files.items()):
            if n.startswith('/') or '..' in Path(n).parts:raise ValueError('unsafe archive name')
            i=zipfile.ZipInfo(n,date_time=(2026,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.create_system=3
            i.external_attr=(0o100755 if n.endswith('.sh') else 0o100644)<<16
            z.writestr(i,b)


def build(output,root=ROOT):
    files,runtime,plugin=public_files(root)
    output=Path(output)
    if output.exists():raise ValueError('output must be a new directory')
    output.mkdir(parents=True)
    stage=output/'public-source'
    for n,b in sorted(files.items()):
        q=stage/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);q.chmod(0o755 if n.endswith('.sh') else 0o644)
    bundles={
      'house-scout-skill-v1.0.0.zip':{'house-scout/'+n:b for n,b in runtime.items()},
      'house-scout-openai-v1.0.0.zip':{n:b for n,b in plugin.items() if not n.startswith(('.claude-plugin/','.codex-plugin/'))},
      'house-scout-claude-v1.0.0.zip':{n:b for n,b in plugin.items() if n!='plugin.json' and not n.startswith('.codex-plugin/')},
      'house-scout-source-v1.0.0.zip':{'house-scout-v1.0.0/'+n:b for n,b in files.items()},
      'house-scout-media-v1.0.0.zip':{n.removeprefix('release/v1.0.0/'):b for n,b in files.items() if n.startswith('release/v1.0.0/assets/')},
    }
    bundles['house-scout-media-v1.0.0.zip']['LICENSE']=files['LICENSE']
    sums={}
    for n,content in bundles.items():
        zip_bytes(output/n,content);sums[n]=hashlib.sha256((output/n).read_bytes()).hexdigest()
    (output/'SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in sorted(sums.items())))
    manifest={'version':VERSION,'publication_status':'prepared_not_published','source_file_count':len(files),
              'files':{n:{'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)} for n,b in sorted(files.items())},'artifacts':sums}
    (output/'public-files.json').write_bytes(encoded(manifest))
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:r=build(a.output)
    except (ValueError,OSError,KeyError,zipfile.BadZipFile) as e:p.exit(2,str(e)+'\n')
    print(json.dumps({'version':VERSION,'files':r['source_file_count'],'output':str(a.output),'artifacts':r['artifacts'],'published':False},indent=2))

if __name__=='__main__':main()
