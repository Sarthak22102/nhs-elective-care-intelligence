#!/usr/bin/env python3
"""Lightweight local pre-publication scan; not a replacement for GitHub secret scanning."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','.venv','__pycache__','.pytest_cache','.ruff_cache'}
TEXT_SUFFIXES={'.py','.md','.sql','.yml','.yaml','.json','.toml','.txt','.csv','.gitignore',''}
PATTERNS={
    'github_token': re.compile(r'github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}'),
    'aws_access_key': re.compile(r'AKIA[0-9A-Z]{16}'),
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'generic_secret_assignment': re.compile(r'(?i)(password|api[_-]?key|secret|token)\s*[=:]\s*["\'][^"\']{8,}["\']'),
    'local_absolute_path': re.compile(r'(?i)(?:/Users/[^/\s]+/|/home/[^/\s]+/|/mnt/data/|[A-Z]:\\Users\\[^\\\s]+\\)'),
}
findings=[]
large=[]
for path in ROOT.rglob('*'):
    if any(part in SKIP for part in path.parts) or not path.is_file():
        continue
    size=path.stat().st_size
    if size > 5*1024*1024:
        large.append((path.relative_to(ROOT),size))
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {'.gitignore'}:
        continue
    try:
        text=path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    for name,pattern in PATTERNS.items():
        if name == 'local_absolute_path' and path.resolve() == Path(__file__).resolve():
            continue
        if pattern.search(text):
            findings.append((path.relative_to(ROOT),name))

print(f'Scanned repository: {ROOT}')
print(f'Potential secret findings: {len(findings)}')
for item in findings:
    print('  ',item)
print(f'Files >5 MiB: {len(large)}')
for item in large:
    print('  ',item)

rc=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT).returncode
if findings or large or rc:
    raise SystemExit(1)
print('Security/build gate passed.')
