from pathlib import Path
from importlib import import_module

def load_subdirs_module(module_name: str):
    root = Path(__file__).parent
    for path in root.iterdir():
        if path.is_file():
            continue
        if (path / f'{module_name}.py').is_file():
            import_module(f'.{path.name}.{module_name}', __package__)
