# extra-hooks/hooks-uvicorn.py
from PyInstaller.utils.hooks import get_package_paths, collect_submodules

datas = [(get_package_paths('uvicorn')[1], 'uvicorn'), (get_package_paths('whitenoise')[1], 'whitenoise')]

hiddenimports = collect_submodules('whitenoise')
