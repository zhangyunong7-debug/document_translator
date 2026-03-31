"""
Translation Application - PyInstaller Entry Point
"""
import sys
import os

# Ensure the app directory is in the path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    app_dir = sys._MEIPASS
    application_path = os.path.dirname(sys.executable)
else:
    # Running as script
    app_dir = os.path.dirname(os.path.abspath(__file__))
    application_path = app_dir

sys.path.insert(0, app_dir)

# Import and run the main application
from translation_app.ui import main

if __name__ == "__main__":
    main()
