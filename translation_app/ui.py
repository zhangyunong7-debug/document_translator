"""
Main UI for the Translation Application
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
from typing import Optional, List

from .config import Config
from .translator import get_engine, SUPPORTED_LANGUAGES
from .word_processor import WordProcessor
from .excel_processor import ExcelProcessor


class TranslationApp:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("文档翻译工具 - Document Translator")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Center window on screen
        self._center_window()

        # Load configuration
        self.config = Config()

        # File paths
        self.selected_files: List[str] = []
        self.output_folder = self.config.get("output_folder", str(Path.home()))

        # Current engine
        self.current_engine_id = self.config.get("selected_engine", "google_free")

        # Setup UI
        self._setup_styles()
        self._create_widgets()
        self._load_settings()

    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_styles(self):
        """Setup custom styles"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Microsoft YaHei", 14, "bold"))
        style.configure("Header.TLabel", font=("Microsoft YaHei", 10, "bold"))
        style.configure("Action.TButton", font=("Microsoft YaHei", 10))

    def _create_widgets(self):
        """Create all UI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ========== Title ==========
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(title_frame, text="文档翻译工具", style="Title.TLabel")
        title_label.pack(side=tk.LEFT)

        # ========== File Selection Section ==========
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        # File list with scrollbar
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill=tk.X, pady=(0, 5))

        self.file_listbox = tk.Listbox(list_frame, height=5, font=("Microsoft YaHei", 9))
        self.file_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # File buttons
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="添加文件", command=self._add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="添加文件夹", command=self._add_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="清除列表", command=self._clear_files).pack(side=tk.LEFT)

        # ========== Translation Settings Section ==========
        settings_frame = ttk.LabelFrame(main_frame, text="翻译设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Engine selection
        engine_frame = ttk.Frame(settings_frame)
        engine_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(engine_frame, text="翻译引擎:").pack(side=tk.LEFT, padx=(0, 5))
        self.engine_var = tk.StringVar(value="google_free")
        engine_combo = ttk.Combobox(
            engine_frame,
            textvariable=self.engine_var,
            values=["google_free: Google Translate (免费)",
                    "google: Google Translate API",
                    "deepl: DeepL API",
                    "baidu: 百度翻译 API"],
            state="readonly",
            width=35
        )
        engine_combo.pack(side=tk.LEFT, padx=(0, 5))
        engine_combo.bind("<<ComboboxSelected>>", self._on_engine_changed)
        self.engine_combo = engine_combo

        ttk.Button(engine_frame, text="配置API密钥", command=self._open_config).pack(side=tk.LEFT)

        # Language selection
        lang_frame = ttk.Frame(settings_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(lang_frame, text="源语言:").pack(side=tk.LEFT, padx=(0, 5))
        self.source_lang_var = tk.StringVar(value="auto")
        source_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.source_lang_var,
            values=[f"{k}: {v}" for k, v in SUPPORTED_LANGUAGES.items()],
            state="readonly",
            width=18
        )
        source_combo.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(lang_frame, text="目标语言:").pack(side=tk.LEFT, padx=(0, 5))
        self.target_lang_var = tk.StringVar(value="zh-CN")
        target_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.target_lang_var,
            values=[f"{k}: {v}" for k, v in SUPPORTED_LANGUAGES.items() if k != "auto"],
            state="readonly",
            width=18
        )
        target_combo.pack(side=tk.LEFT)

        # Output folder selection
        output_frame = ttk.Frame(settings_frame)
        output_frame.pack(fill=tk.X)

        ttk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_var = tk.StringVar(value=self.output_folder)
        ttk.Entry(output_frame, textvariable=self.output_var, width=50).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(output_frame, text="浏览", command=self._select_output_folder).pack(side=tk.LEFT)

        # ========== Translate Button ==========
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.translate_btn = ttk.Button(
            btn_frame,
            text="开始翻译",
            command=self._start_translation,
            style="Action.TButton"
        )
        self.translate_btn.pack(fill=tk.X, pady=(0, 5))

        # ========== Progress Section ==========
        progress_frame = ttk.LabelFrame(main_frame, text="进度", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        # Status label
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W)

        # Log area
        log_frame = ttk.Frame(progress_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Consolas", 9),
            state='disabled'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _load_settings(self):
        """Load settings from config"""
        # Load engine
        engine_map = {
            "google_free": 0,
            "google": 1,
            "deepl": 2,
            "baidu": 3
        }
        if self.current_engine_id in engine_map:
            self.engine_combo.current(engine_map[self.current_engine_id])

        # Load languages
        source_lang = self.config.get("default_source_lang", "auto")
        target_lang = self.config.get("default_target_lang", "zh-CN")
        self.source_lang_var.set(source_lang)
        self.target_lang_var.set(target_lang)

        # Load output folder
        self.output_var.set(self.output_folder)

    def _add_files(self):
        """Add files to the list"""
        files = filedialog.askopenfilenames(
            title="选择文档",
            filetypes=[
                ("支持的文档", "*.docx *.xlsx"),
                ("Word文档", "*.docx"),
                ("Excel文件", "*.xlsx"),
                ("所有文件", "*.*")
            ]
        )

        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))
            self._log(f"已添加 {len(files)} 个文件")

    def _add_folder(self):
        """Add all files from a folder"""
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            count = 0
            for ext in ['*.docx', '*.xlsx']:
                for file in Path(folder).glob(ext):
                    if str(file) not in self.selected_files:
                        self.selected_files.append(str(file))
                        self.file_listbox.insert(tk.END, file.name)
                        count += 1
            self._log(f"已添加 {count} 个文件")

    def _clear_files(self):
        """Clear the file list"""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self._log("已清除文件列表")

    def _select_output_folder(self):
        """Select output folder"""
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_folder = folder
            self.output_var.set(folder)
            self.config.set("output_folder", folder)
            self.config.save_config()

    def _on_engine_changed(self, event=None):
        """Handle engine selection change"""
        selection = self.engine_var.get()
        engine_id = selection.split(":")[0]
        self.current_engine_id = engine_id
        self.config.set("selected_engine", engine_id)
        self.config.save_config()

    def _open_config(self):
        """Open configuration dialog"""
        ConfigDialog(self.root, self.config, self.current_engine_id)

    def _start_translation(self):
        """Start the translation process"""
        if not self.selected_files:
            messagebox.showwarning("提示", "请先添加要翻译的文件")
            return

        # Validate engine
        engine = get_engine(self.current_engine_id, self.config)
        if not engine:
            messagebox.showerror("错误", "无法加载翻译引擎")
            return

        # Check if engine is configured (except free engine)
        if self.current_engine_id != "google_free" and not engine.is_configured():
            messagebox.showwarning("配置未完成",
                                   f"请先配置 {engine.get_name()} 的API密钥")
            self._open_config()
            return

        # Get language settings
        source_lang = self.source_lang_var.get()
        target_lang = self.target_lang_var.get()

        if source_lang == target_lang:
            messagebox.showwarning("提示", "源语言和目标语言不能相同")
            return

        # Start translation in background thread
        self.translate_btn.config(state='disabled')
        thread = threading.Thread(
            target=self._translate_files,
            args=(engine, source_lang, target_lang),
            daemon=True
        )
        thread.start()

    def _translate_files(self, engine, source_lang: str, target_lang: str):
        """Translate files in background thread"""
        total_files = len(self.selected_files)
        success_count = 0
        error_count = 0

        for index, file_path in enumerate(self.selected_files):
            self._log(f"\n[{index + 1}/{total_files}] 正在翻译: {os.path.basename(file_path)}")
            self.status_var.set(f"正在翻译: {os.path.basename(file_path)}")

            try:
                self._translate_single_file(file_path, engine, source_lang, target_lang)
                success_count += 1
                self._log(f"✓ 完成: {os.path.basename(file_path)}")
            except Exception as e:
                error_count += 1
                self._log(f"✗ 失败: {os.path.basename(file_path)} - {str(e)}")

            # Update progress
            progress = ((index + 1) / total_files) * 100
            self.root.after(0, lambda p=progress: self.progress_var.set(p))

        # Complete
        self.root.after(0, lambda: self.translate_btn.config(state='normal'))
        self.root.after(0, lambda: self.status_var.set(f"完成! 成功: {success_count}, 失败: {error_count}"))
        self._log(f"\n翻译完成! 成功: {success_count}, 失败: {error_count}")

        if success_count > 0:
            self.root.after(0, lambda: messagebox.showinfo(
                "完成",
                f"翻译完成！\n成功: {success_count} 个文件\n失败: {error_count} 个文件\n\n输出目录: {self.output_folder}"
            ))

    def _translate_single_file(self, file_path: str, engine, source_lang: str, target_lang: str):
        """Translate a single file"""
        file_ext = Path(file_path).suffix.lower()

        # Determine output path
        original_name = Path(file_path).stem
        output_name = f"{original_name}_translated{file_ext}"
        output_path = Path(self.output_folder) / output_name

        # Progress callback
        def progress_callback(current, total):
            percent = (current / total) * 100
            self._log(f"  进度: {current}/{total} ({percent:.1f}%)")

        if file_ext == '.docx':
            processor = WordProcessor(file_path)
            processor.load()
            processor.translate_content(engine, source_lang, target_lang, progress_callback)
            processor.save(str(output_path))
        elif file_ext == '.xlsx':
            processor = ExcelProcessor(file_path)
            processor.load()
            processor.translate_content(engine, source_lang, target_lang, progress_callback)
            processor.save(str(output_path))
        else:
            raise Exception("不支持的文件格式")

    def _log(self, message: str):
        """Add message to log"""
        def update_log():
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')

        self.root.after(0, update_log)


class ConfigDialog:
    """Configuration dialog for API keys"""

    def __init__(self, parent, config: Config, current_engine: str):
        self.config = config
        self.current_engine = current_engine
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("API密钥配置")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"500x350+{x}+{y}")

        self._create_widgets()
        self._load_values()

    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Google Translate API
        ttk.Label(main_frame, text="Google Translate API:", font=("Microsoft YaHei", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(main_frame, text="(可选) 付费版本，支持更多语言和更高配额",
                  foreground="gray").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Label(main_frame, text="API Key:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.google_key = ttk.Entry(main_frame, width=50)
        self.google_key.grid(row=3, column=0, sticky=tk.EW, pady=(0, 20))

        # DeepL API
        ttk.Label(main_frame, text="DeepL API:", font=("Microsoft YaHei", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(main_frame, text="(可选) 高质量翻译，支持多种欧洲和亚洲语言",
                  foreground="gray").grid(row=5, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Label(main_frame, text="API Key:").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.deepl_key = ttk.Entry(main_frame, width=50)
        self.deepl_key.grid(row=7, column=0, sticky=tk.EW, pady=(0, 20))

        # Baidu Translate API
        ttk.Label(main_frame, text="百度翻译 API:", font=("Microsoft YaHei", 10, "bold")).grid(
            row=8, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(main_frame, text="(可选) 百度翻译开放平台，需要申请应用",
                  foreground="gray").grid(row=9, column=0, sticky=tk.W, pady=(0, 10))

        baidu_frame = ttk.Frame(main_frame)
        baidu_frame.grid(row=10, column=0, sticky=tk.EW, pady=(0, 20))

        ttk.Label(baidu_frame, text="App ID:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.baidu_appid = ttk.Entry(baidu_frame, width=25)
        self.baidu_appid.grid(row=0, column=1, padx=(10, 20))

        ttk.Label(baidu_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W)
        self.baidu_key = ttk.Entry(baidu_frame, width=25)
        self.baidu_key.grid(row=1, column=1, padx=(10, 0))

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=11, column=0, sticky=tk.EW, pady=(10, 0))

        ttk.Button(btn_frame, text="保存", command=self._save).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.RIGHT)

        main_frame.columnconfigure(0, weight=1)

    def _load_values(self):
        """Load current config values"""
        self.google_key.insert(0, self.config.get("google_api_key", ""))
        self.deepl_key.insert(0, self.config.get("deepl_api_key", ""))
        self.baidu_appid.insert(0, self.config.get("baidu_app_id", ""))
        self.baidu_key.insert(0, self.config.get("baidu_api_key", ""))

    def _save(self):
        """Save configuration"""
        self.config.set("google_api_key", self.google_key.get().strip())
        self.config.set("deepl_api_key", self.deepl_key.get().strip())
        self.config.set("baidu_app_id", self.baidu_appid.get().strip())
        self.config.set("baidu_api_key", self.baidu_key.get().strip())
        self.config.save_config()

        messagebox.showinfo("保存成功", "配置已保存")
        self.dialog.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()

    # Set icon (optional, will use default if not found)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass

    app = TranslationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
