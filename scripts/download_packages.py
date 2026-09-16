"""Download wheels for an offline Windows x64 computer matching this Python."""

import argparse
from pathlib import Path
import platform
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--runtime-only', action='store_true',
                        help='Exclude EXE build dependencies.')
    args = parser.parse_args()
    if sys.platform != 'win32' or platform.machine().lower() not in ('amd64', 'x86_64'):
        parser.error('Run on Windows x64 so dependency markers match the target.')
    if platform.python_implementation() != 'CPython':
        parser.error('CPython is required.')
    root = Path(__file__).resolve().parents[1]
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    requirements = destination / 'requirements.txt'
    version = f'{sys.version_info.major}.{sys.version_info.minor}'
    abi = f'cp{sys.version_info.major}{sys.version_info.minor}'
    print(f'Target: Windows x64, CPython {version}, ABI {abi}', flush=True)
    export = ['uv', 'export', '--locked', '--format', 'requirements-txt',
              '--no-default-groups', '--no-hashes', '--no-emit-project',
              '--output-file', str(requirements)]
    if not args.runtime_only:
        export += ['--group', 'build']
    subprocess.run(export, cwd=root, check=True)
    subprocess.run([sys.executable, '-m', 'pip', 'download',
                    '-r', str(requirements), '-d', str(destination),
                    '--platform', 'win_amd64', '--python-version', version,
                    '--implementation', 'cp', '--abi', abi,
                    '--only-binary=:all:'], cwd=root, check=True)
    print(f'Packages saved to {destination}. Target computer needs Python {version} x64.')


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as error:
        print('Download incomplete. Resolve the error above and run again.', file=sys.stderr)
        raise SystemExit(error.returncode)
