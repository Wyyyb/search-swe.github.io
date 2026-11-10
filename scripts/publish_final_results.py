#!/usr/bin/env python3
"""Prepare the final Luna/Terra/Sol release and optionally upload it to HF.

Without --upload, prepare and validate locally. With --upload, resume the public
upload, verify it and build production pages. Existing HF releases are retained.
Git commit and push are separate steps. Uses the existing HF login.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from import_final_results import DEFAULT_FINAL, DEFAULT_PACKAGE, install_preview, prepare
from import_results import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final-dir', type=Path, default=DEFAULT_FINAL)
    parser.add_argument('--package', type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument('--upload', action='store_true')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    package = args.package.resolve()
    snapshot, manifest = prepare(args.final_dir, package)
    install_preview(package, snapshot, manifest)
    command = [sys.executable, str(ROOT / 'scripts/upload_hf_release.py'),
               '--package', str(package), '--workers', str(args.workers)]
    if args.upload:
        command.append('--upload')
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
