import os, sys
from pathlib import Path

"""
    Define all path
"""


FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # src root
WS_ROOT = FILE.parents[2]

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

if str(WS_ROOT) not in sys.path:
    sys.path.append(str(WS_ROOT))  # add ROOT to PATH

ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
WS_ROOT = Path(os.path.relpath(WS_ROOT, Path.cwd()))

TEMP_PATH = os.path.join(Path.cwd(),'output')
os.makedirs(TEMP_PATH, exist_ok=True)
print(TEMP_PATH)
AI_MODULE_PATH = os.path.join(Path.cwd(), 'ai_module')
print(AI_MODULE_PATH)