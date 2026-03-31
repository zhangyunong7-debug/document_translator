"""
cx_Freeze setup script for Document Translator
"""
from cx_Freeze import setup, Executable
import sys

# Build options
build_options = {
    'packages': [
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'docx',
        'openpyxl',
        'requests',
        'deep_translator',
        'pyperclip',
        'PIL',
    ],
    'excludes': [
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PyQt5',
        'PyQt6',
    ],
    'optimize': 2,
}

# Base executable
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'  # No console window

# Executables
executables = [
    Executable(
        'main.py',
        base=base,
        target_name='DocumentTranslator.exe',
        icon=None,
        shortcut_name='Document Translator',
        shortcut_dir='Desktop',
    )
]

# Setup
setup(
    name='DocumentTranslator',
    version='1.0.0',
    description='Document Translation Tool for Word and Excel',
    author='Document Translator',
    options={'build_exe': build_options},
    executables=executables,
)
