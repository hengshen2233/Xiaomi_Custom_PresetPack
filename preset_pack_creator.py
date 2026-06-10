import os
import shutil
import zipfile
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class PresetPackCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("预设包制作工具")
        self.root.geometry("900x700")
        
        self.default_dir = os.path.join(os.path.dirname(__file__), "Default")
        self.output_dir = os.path.join(os.path.dirname(__file__), "预设包")
        
        self.params = {
            "自动曝光": {"file": "p_pref_camera_autoexposure", "value": "1", "type": "select", "options": ["0", "1"]},
            "镜头": {"file": "p_pref_camera_manually_lens", "value": "wide", "type": "select", "options": ["wide", "tele"]},
            "场景类型": {"file": "p_pref_camera_cv_type", "value": "0", "type": "select", "options": ["0", "1"]},
            "格式": {"file": "p_pref_camera_raw", "value": "JPEG", "type": "select", "options": ["JPEG", "RAW"]},
            "超清像素": {"file": "p_pref_ultra_pixel_167", "value": "BYPASS", "type": "select", "options": ["BYPASS", "ON"]},
            "白平衡": {"file": "p_pref_camera_whitebalance", "value": "1", "type": "int"},
            "变焦倍率": {"file": "p_pref_camera_zoom_retain", "value": "1.0", "type": "float1"},
            "对焦位置": {"file": "p_pref_focus_position", "value": "1000", "type": "int"},
            "快门速度": {"file": "p_pref_qc_camera_exposuretime", "value": "0", "type": "int"},
            "感光度": {"file": "p_pref_qc_camera_iso", "value": "0", "type": "int"},
            "曝光补偿": {"file": "p_pref_qc_camera_pro_exposure_value", "value": "0", "type": "float0"},
            "色温": {"file": "p_pref_qc_camera_style_color_temp", "value": "0", "type": "int"},
            "色调": {"file": "p_pref_qc_camera_style_color_tone", "value": "0", "type": "int"},
            "纹理": {"file": "p_pref_qc_camera_style_texture", "value": "0", "type": "int"},
            "影调": {"file": "p_pref_qc_camera_style_tone", "value": "0", "type": "int"},
            "饱和度": {"file": "p_pref_qc_camera_style_vibrance", "value": "0", "type": "int"}
        }
        
        self.entries = {}
        self.create_widgets()
    
    def validate_float1(self, value):
        if value == "":
            return True
        try:
            num = float(value)
            if num < 0 or num > 10:
                return False
            parts = value.split('.')
            if len(parts) > 2:
                return False
            if len(parts) == 2 and len(parts[1]) > 1:
                return False
            return True
        except ValueError:
            return False
    
    def format_float1(self, value):
        try:
            num = float(value)
            return f"{num:.1f}"
        except ValueError:
            return value

    def validate_float0(self, value):
        if value == "":
            return True
        try:
            float(value)
            parts = value.split('.')
            if len(parts) > 2:
                return False
            if len(parts) == 2 and len(parts[1]) > 1:
                return False
            return True
        except ValueError:
            return False

    def format_float0(self, value):
        try:
            num = float(value)
            if num == int(num):
                return f"{int(num)}"
            else:
                return f"{num:.1f}"
        except ValueError:
            return value

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        title_label = ttk.Label(main_frame, text="预设包制作工具", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        left_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        row = 0
        for param_name, param_info in self.params.items():
            label = ttk.Label(left_frame, text=param_name)
            label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
            
            if param_info["type"] == "select":
                combo = ttk.Combobox(left_frame, values=param_info["options"], width=22)
                combo.set(param_info["value"])
                combo.grid(row=row, column=1, padx=5, pady=3)
                self.entries[param_name] = combo
            else:
                entry = ttk.Entry(left_frame, width=24)
                entry.insert(0, param_info["value"])
                entry.grid(row=row, column=1, padx=5, pady=3)
                
                if param_info["type"] == "float1":
                    vcmd = (self.root.register(self.validate_float1), '%P')
                    entry.config(validate='key', validatecommand=vcmd)
                elif param_info["type"] == "float0":
                    vcmd = (self.root.register(self.validate_float0), '%P')
                    entry.config(validate='key', validatecommand=vcmd)
                
                entry.default_value = param_info["value"]
                self.entries[param_name] = entry
            row += 1
        
        right_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        ttk.Label(right_frame, text="预设包名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.preset_name_entry = ttk.Entry(right_frame, width=30)
        self.preset_name_entry.insert(0, "我的预设")
        self.preset_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(right_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir_entry = ttk.Entry(right_frame, width=30)
        self.output_dir_entry.insert(0, self.output_dir)
        self.output_dir_entry.grid(row=1, column=1, padx=5, pady=5)
        
        browse_btn = ttk.Button(right_frame, text="浏览", command=self.browse_output_dir)
        browse_btn.grid(row=1, column=2, padx=5, pady=5)
        
        preview_label = ttk.Label(right_frame, text="生成的文件预览:")
        preview_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.preview_text = tk.Text(right_frame, width=50, height=20, wrap=tk.WORD)
        self.preview_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        
        generate_btn = ttk.Button(main_frame, text="生成预设包", command=self.generate_preset_pack, style='Accent.TButton')
        generate_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 12, 'bold'))
        
        self.update_preview()
    
    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(initialdir=self.output_dir)
        if dir_path:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, dir_path)
    
    def update_preview(self):
        self.preview_text.delete(1.0, tk.END)
        files = []
        
        for param_name, param_info in self.params.items():
            if param_name in self.entries:
                if isinstance(self.entries[param_name], ttk.Combobox):
                    value = self.entries[param_name].get()
                else:
                    value = self.entries[param_name].get()
                
                if param_info["type"] == "float1":
                    value = self.format_float1(value)
                elif param_info["type"] == "float0":
                    value = self.format_float0(value)
                
                file_name = param_info["file"]
                if param_name == "镜头":
                    new_name = f"{file_name}_{value}"
                elif param_name == "超清像素":
                    new_name = f"{file_name}_{value}"
                elif param_name == "白平衡":
                    new_name = f"{file_name}_key_new_{value}"
                else:
                    new_name = f"{file_name}_key_{value}"
                files.append(new_name)
        
        files.append("ac")
        files.append("t")
        files.append("v_3")
        
        for f in sorted(files):
            self.preview_text.insert(tk.END, f + "\n")
    
    def generate_preset_pack(self):
        preset_name = self.preset_name_entry.get().strip()
        if not preset_name:
            messagebox.showerror("错误", "请输入预设包名称")
            return
        
        output_base_dir = self.output_dir_entry.get().strip()
        if not output_base_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        zip_path = os.path.join(output_base_dir, f"Manual_official_0_{preset_name}.zip")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                for param_name, param_info in self.params.items():
                    src_file = os.path.join(self.default_dir, param_info["file"])
                    
                    if isinstance(self.entries[param_name], ttk.Combobox):
                        value = self.entries[param_name].get()
                    else:
                        value = self.entries[param_name].get()
                    
                    if param_info["type"] == "float1":
                        value = self.format_float1(value)
                    elif param_info["type"] == "float0":
                        value = self.format_float0(value)
                    
                    if param_name == "镜头":
                        dst_name = f"{param_info['file']}_{value}"
                    elif param_name == "超清像素":
                        dst_name = f"{param_info['file']}_{value}"
                    elif param_name == "白平衡":
                        dst_name = f"{param_info['file']}_key_new_{value}"
                    else:
                        dst_name = f"{param_info['file']}_key_{value}"
                    
                    dst_file = os.path.join(temp_dir, dst_name)
                    
                    if os.path.exists(src_file):
                        shutil.copy2(src_file, dst_file)
                
                for static_file in ["ac", "t", "v_3"]:
                    src_file = os.path.join(self.default_dir, static_file)
                    if os.path.exists(src_file):
                        shutil.copy2(src_file, os.path.join(temp_dir, static_file))
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
            
            messagebox.showinfo("成功", f"预设包 'Manual_official_0_{preset_name}.zip' 已生成!\n\n输出路径:\n{zip_path}")
        
        except Exception as e:
            messagebox.showerror("错误", f"生成预设包时发生错误:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PresetPackCreator(root)
    
    def on_entry_change(*args):
        app.update_preview()
    
    def on_float1_focus_out(event):
        entry = event.widget
        value = entry.get()
        if value:
            formatted = app.format_float1(value)
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
            app.update_preview()
        else:
            entry.delete(0, tk.END)
            entry.insert(0, entry.default_value)
            app.update_preview()

    def on_float0_focus_out(event):
        entry = event.widget
        value = entry.get()
        if value:
            formatted = app.format_float0(value)
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
            app.update_preview()
        else:
            entry.delete(0, tk.END)
            entry.insert(0, entry.default_value)
            app.update_preview()

    def on_int_focus_out(event):
        entry = event.widget
        value = entry.get()
        if not value:
            entry.delete(0, tk.END)
            entry.insert(0, entry.default_value)
            app.update_preview()

    for param_name, entry in app.entries.items():
        if isinstance(entry, ttk.Entry):
            entry.bind('<KeyRelease>', on_entry_change)
            if app.params[param_name]["type"] == "float1":
                entry.bind('<FocusOut>', on_float1_focus_out)
            elif app.params[param_name]["type"] == "float0":
                entry.bind('<FocusOut>', on_float0_focus_out)
            else:
                entry.bind('<FocusOut>', on_int_focus_out)
        elif isinstance(entry, ttk.Combobox):
            entry.bind('<<ComboboxSelected>>', on_entry_change)
    
    root.mainloop()