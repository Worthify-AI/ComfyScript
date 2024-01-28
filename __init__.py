__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

success = True

import sys
from pathlib import Path

if sys.version_info < (3, 9):
    success = False
    print('\033[34mComfyScript: \033[91mPython 3.9+ is required.\033[0m')

try:
    print('\033[34mComfyScript: \033[93mLoading nodes...\033[0m')
    # If there are conflicts, the later one will override the former one.

    from .nodes import ComfyUI_Ib_CustomNodes
    NODE_CLASS_MAPPINGS.update(ComfyUI_Ib_CustomNodes.NODE_CLASS_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(ComfyUI_Ib_CustomNodes.NODE_DISPLAY_NAME_MAPPINGS)

    from .nodes import comfyui_tooling_nodes
    NODE_CLASS_MAPPINGS.update(comfyui_tooling_nodes.NODE_CLASS_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(comfyui_tooling_nodes.NODE_DISPLAY_NAME_MAPPINGS)
except (ImportError, AttributeError) as e:
    success = False
    print(
f'''\033[34mComfyScript: \033[91mFailed to load nodes due to missing submodules: {e}.
If you need them, try to run:
git -C "{Path(__file__).resolve().parent}" submodule update --init --recursive
\033[0m''')

src = Path(__file__).resolve().parent / 'src'
sys.path.insert(0, str(src))
import comfy_script
success &= comfy_script.import_as_node

if success:
    print('\033[34mComfyScript: \033[92mLoaded\033[0m')
