#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    for path in [*root.glob('scripts/*.py'), *root.glob('tests/*.py')]:
        compile(path.read_text(), str(path), 'exec')
    for path in (root / '.codex-plugin/plugin.json', root / 'hooks/hooks.json', root / 'config/models.default.json', root / '.agents/plugins/marketplace.json'):
        json.loads(path.read_text())
    import model_config
    model_config.validate(json.loads((root / 'config/models.default.json').read_text()))
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=root, env=environment, check=True)
    print('Source syntax, JSON, default model schema, and tests passed.')


if __name__ == '__main__':
    main()
