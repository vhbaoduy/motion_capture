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
PATH_TO_DATA = os.path.join(WS_ROOT, 'modeling', 'extra_data')

DEFAULT_CHECKPOINT_PATH_SMPL = "modeling/extra_data/body_module/pretrained_weights/2020_05_31-00_50_43-best-51.749683916568756.pt"
DEFAULT_CHECKPOINT_PATH_SMPLX = "modeling/extra_data/body_module/pretrained_weights/smplx-03-28-46060-w_spin_mlc3d_46582-2089_2020_03_28-21_56_16.pt"

TEMP_DIR = "tmp"
SAVE_PATH = os.path.join(WS_ROOT, TEMP_DIR)
os.makedirs(SAVE_PATH, exist_ok=True)
