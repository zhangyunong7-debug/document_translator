@echo off
chcp 65001 >nul
echo ============================================
echo    文档翻译工具 - 一键构建脚本
echo ============================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python 3.8+
    echo 请先从 https://www.python.org/downloads/ 安装Python
    pause
    exit /b 1
)

:: 检查pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到pip，请确保安装Python时勾选了pip
    pause
    exit /b 1
)

:: 创建构建目录
echo [步骤1/4] 准备构建环境...
if not exist "build" mkdir build
if not exist "dist" mkdir dist

:: 安装依赖
echo.
echo [步骤2/4] 安装依赖包...
pip install python-docx openpyxl requests deep-translator pyperclip Pillow -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

:: 安装PyInstaller
echo.
echo [步骤3/4] 安装打包工具...
pip install pyinstaller -q
if errorlevel 1 (
    echo [错误] PyInstaller安装失败
    pause
    exit /b 1
)

:: 开始打包
echo.
echo [步骤4/4] 打包应用程序...
echo.

pyinstaller ^
    --name="DocumentTranslator" ^
    --onefile ^
    --windowed ^
    --icon=NUL ^
    --add-binary=".";"." ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.scrolledtext ^
    --hidden-import=docx ^
    --hidden-import=openpyxl ^
    --hidden-import=requests ^
    --hidden-import=deep_translator ^
    --hidden-import=pyperclip ^
    --exclude-module=matplotlib ^
    --exclude-module=numpy ^
    --exclude-module=pandas ^
    --exclude-module=scipy ^
    main.py --clean

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ============================================
echo    构建完成！
echo ============================================
echo.
echo 可执行文件位置:
echo   dist\DocumentTranslator.exe
echo.
echo 按任意键打开输出目录...
pause >nul
explorer dist
