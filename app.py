import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import sys
import os
from datetime import datetime, timedelta
from openpyxl import load_workbook
import glob

def get_base_path():
    if getattr(sys, 'frozen', False):
        if sys.platform == 'darwin':
            return os.path.dirname(os.path.dirname(sys.executable))
        else:
            return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_python_executable():
    base_path = get_base_path()
    venv_python = os.path.join(base_path, "venv", "bin", "python")
    if os.path.exists(venv_python):
        return venv_python
    venv_python_win = os.path.join(base_path, "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python_win):
        return venv_python_win
    return sys.executable

class BlogAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("네이버 블로그 자동화 도구")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        
        self.log_file_path = os.path.join(get_base_path(), "app_log.txt")
        
        container = tk.Frame(root, bg='#f0f0f0')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(
            container, 
            text="네이버 블로그 자동화 도구", 
            font=("Helvetica", 20, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(0, 30))
        
        button_container = tk.Frame(container, bg='#f0f0f0')
        button_container.pack(fill=tk.X, pady=10)
        
        self.btn_create_excel = tk.Button(
            button_container, 
            text="1. 엑셀 파일 생성",
            command=self.create_excel,
            width=25,
            height=2,
            font=("Helvetica", 12),
            bg='#4CAF50',
            fg='white'
        )
        self.btn_create_excel.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.btn_generate_content = tk.Button(
            button_container,
            text="2. 블로그 본문 생성",
            command=self.generate_content,
            width=25,
            height=2,
            font=("Helvetica", 12),
            bg='#2196F3',
            fg='white'
        )
        self.btn_generate_content.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        button_container2 = tk.Frame(container, bg='#f0f0f0')
        button_container2.pack(fill=tk.X, pady=10)
        
        self.btn_upload = tk.Button(
            button_container2,
            text="3. 블로그 업로드",
            command=self.upload_blog,
            width=25,
            height=2,
            font=("Helvetica", 12),
            bg='#FF9800',
            fg='white'
        )
        self.btn_upload.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.btn_run_all = tk.Button(
            button_container2,
            text="전체 실행 (1→2→3)",
            command=self.run_all,
            width=25,
            height=2,
            font=("Helvetica", 12, "bold"),
            bg='#9C27B0',
            fg='white'
        )
        self.btn_run_all.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        schedule_container = tk.LabelFrame(
            container,
            text="예약 발행 설정",
            font=("Helvetica", 11, "bold"),
            bg='#f0f0f0',
            fg='#333333',
            padx=10,
            pady=10
        )
        schedule_container.pack(fill=tk.X, pady=10)
        
        self.schedule_enabled = tk.BooleanVar(value=False)
        schedule_check = tk.Checkbutton(
            schedule_container,
            text="예약 발행 사용",
            variable=self.schedule_enabled,
            font=("Helvetica", 11),
            bg='#f0f0f0',
            command=self.toggle_schedule_options
        )
        schedule_check.pack(anchor=tk.W)
        
        self.schedule_options_frame = tk.Frame(schedule_container, bg='#f0f0f0')
        self.schedule_options_frame.pack(fill=tk.X, pady=(10, 0))
        
        date_frame = tk.Frame(self.schedule_options_frame, bg='#f0f0f0')
        date_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(date_frame, text="시작 날짜:", font=("Helvetica", 10), bg='#f0f0f0', width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.start_date = tk.Entry(date_frame, width=12, font=("Helvetica", 10))
        self.start_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.start_date.pack(side=tk.LEFT, padx=5)
        tk.Label(date_frame, text="(YYYY-MM-DD)", font=("Helvetica", 9), bg='#f0f0f0', fg='#666666').pack(side=tk.LEFT)
        
        time_frame = tk.Frame(self.schedule_options_frame, bg='#f0f0f0')
        time_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(time_frame, text="시작 시간:", font=("Helvetica", 10), bg='#f0f0f0', width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.start_hour = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(24)], width=4, font=("Helvetica", 10))
        self.start_hour.set("09")
        self.start_hour.pack(side=tk.LEFT, padx=2)
        tk.Label(time_frame, text="시", font=("Helvetica", 10), bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.start_minute = ttk.Combobox(time_frame, values=["00", "10", "20", "30", "40", "50"], width=4, font=("Helvetica", 10))
        self.start_minute.set("00")
        self.start_minute.pack(side=tk.LEFT, padx=2)
        tk.Label(time_frame, text="분", font=("Helvetica", 10), bg='#f0f0f0').pack(side=tk.LEFT)
        
        interval_frame = tk.Frame(self.schedule_options_frame, bg='#f0f0f0')
        interval_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(interval_frame, text="글 간격:", font=("Helvetica", 10), bg='#f0f0f0', width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.interval_minutes = tk.Spinbox(interval_frame, from_=10, to=1440, increment=10, width=5, font=("Helvetica", 10))
        self.interval_minutes.delete(0, tk.END)
        self.interval_minutes.insert(0, "30")
        self.interval_minutes.pack(side=tk.LEFT, padx=2)
        tk.Label(interval_frame, text="분 간격으로 발행", font=("Helvetica", 10), bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.toggle_schedule_options()
        
        progress_container = tk.LabelFrame(
            container, 
            text="진행 상황", 
            font=("Helvetica", 11, "bold"),
            bg='#f0f0f0',
            fg='#333333',
            padx=10,
            pady=10
        )
        progress_container.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.StringVar(value="대기 중...")
        self.progress_label = tk.Label(
            progress_container, 
            textvariable=self.progress_var, 
            font=("Helvetica", 11),
            bg='#f0f0f0',
            fg='#333333',
            anchor=tk.W
        )
        self.progress_label.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_container, 
            mode='indeterminate', 
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        log_container = tk.LabelFrame(
            container, 
            text="실행 로그", 
            font=("Helvetica", 11, "bold"),
            bg='#f0f0f0',
            fg='#333333',
            padx=10,
            pady=10
        )
        log_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container, 
            height=15, 
            width=70, 
            wrap=tk.WORD, 
            font=("Courier", 10),
            bg='white',
            fg='#333333'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        log_button_frame = tk.Frame(log_container, bg='#f0f0f0')
        log_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        btn_copy_log = tk.Button(
            log_button_frame,
            text="로그 복사",
            command=self.copy_log,
            font=("Helvetica", 10),
            bg='#607D8B',
            fg='white'
        )
        btn_copy_log.pack(side=tk.LEFT, padx=2)
        
        btn_clear_log = tk.Button(
            log_button_frame,
            text="로그 지우기",
            command=self.clear_log,
            font=("Helvetica", 10),
            bg='#9E9E9E',
            fg='white'
        )
        btn_clear_log.pack(side=tk.LEFT, padx=2)
        
        self.status_var = tk.StringVar(value="준비됨")
        status_label = tk.Label(
            container, 
            textvariable=self.status_var, 
            anchor=tk.W,
            font=("Helvetica", 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        status_label.pack(fill=tk.X, pady=5)
        
        self.log("애플리케이션이 시작되었습니다.")
        self.log("버튼을 클릭하여 작업을 시작하세요.")
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        self.log_text.insert(tk.END, f"{log_line}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(f"{log_line}\n")
    
    def copy_log(self):
        log_content = self.log_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        messagebox.showinfo("복사 완료", "로그가 클립보드에 복사되었습니다.")
    
    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
    
    def toggle_schedule_options(self):
        state = tk.NORMAL if self.schedule_enabled.get() else tk.DISABLED
        for child in self.schedule_options_frame.winfo_children():
            for widget in child.winfo_children():
                if isinstance(widget, (tk.Entry, ttk.Combobox, tk.Spinbox)):
                    widget.config(state=state)
        
    def update_status(self, message):
        self.status_var.set(message)
        self.progress_var.set(message)
        self.root.update_idletasks()
        
    def set_buttons_state(self, state):
        self.btn_create_excel.config(state=state)
        self.btn_generate_content.config(state=state)
        self.btn_upload.config(state=state)
        self.btn_run_all.config(state=state)
        
    def run_script(self, script_name, description):
        def run():
            try:
                self.update_status(f"{description} 실행 중...")
                self.progress_bar.start(10)
                self.log(f"{description} 시작")
                
                base_path = get_base_path()
                script_path = os.path.join(base_path, script_name)
                
                if not os.path.exists(script_path):
                    script_path = script_name
                
                python_exe = get_python_executable()
                process = subprocess.Popen(
                    [python_exe, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=base_path
                )
                
                for line in process.stdout:
                    if line.strip():
                        self.log(line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.update_status(f"{description} 완료")
                    self.log(f"{description} 성공적으로 완료되었습니다.")
                    messagebox.showinfo("완료", f"{description}가 완료되었습니다.")
                else:
                    self.update_status(f"{description} 실패")
                    self.log(f"{description} 실행 중 오류가 발생했습니다.")
                    messagebox.showerror("오류", f"{description} 실행 중 오류가 발생했습니다.")
                    
            except Exception as e:
                self.update_status(f"{description} 오류")
                self.log(f"오류: {str(e)}")
                messagebox.showerror("오류", f"오류 발생: {str(e)}")
            finally:
                self.progress_bar.stop()
                self.set_buttons_state(tk.NORMAL)
        
        self.set_buttons_state(tk.DISABLED)
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
    def create_excel(self):
        self.run_script("excel_create.py", "엑셀 파일 생성")
        
    def generate_content(self):
        self.run_script("create.py", "블로그 본문 생성")
        
    def update_excel_schedule(self):
        """예약 발행 설정에 따라 엑셀 D열 업데이트"""
        if not self.schedule_enabled.get():
            return True
        
        try:
            base_path = get_base_path()
            pattern = os.path.join(base_path, "blog*.xlsx")
            files = glob.glob(pattern)
            
            if not files:
                self.log("엑셀 파일을 찾을 수 없습니다.")
                return False
            
            excel_file = max(files, key=os.path.getmtime)
            self.log(f"예약 시간 설정 중: {excel_file}")
            
            wb = load_workbook(excel_file)
            ws = wb.active
            
            start_date_str = self.start_date.get()
            start_hour = self.start_hour.get()
            start_minute = self.start_minute.get()
            interval = int(self.interval_minutes.get())
            
            start_datetime = datetime.strptime(f"{start_date_str} {start_hour}:{start_minute}", "%Y-%m-%d %H:%M")
            
            row_count = 0
            for row in range(2, ws.max_row + 1):
                title = ws[f'A{row}'].value
                content = ws[f'B{row}'].value
                
                if title and content:
                    schedule_time = start_datetime + timedelta(minutes=interval * row_count)
                    ws[f'D{row}'] = schedule_time.strftime("%Y-%m-%d %H:%M")
                    self.log(f"  {row}행: {schedule_time.strftime('%Y-%m-%d %H:%M')}")
                    row_count += 1
            
            wb.save(excel_file)
            wb.close()
            self.log(f"총 {row_count}개 글에 예약 시간 설정 완료")
            return True
            
        except Exception as e:
            self.log(f"예약 시간 설정 오류: {e}")
            return False
    
    def upload_blog(self):
        if self.schedule_enabled.get():
            if not self.update_excel_schedule():
                messagebox.showerror("오류", "예약 시간 설정 중 오류가 발생했습니다.")
                return
        self.run_script("upload_bot.py", "블로그 업로드")
        
    def run_all(self):
        def run_all_scripts():
            try:
                self.progress_bar.start(10)
                base_path = get_base_path()
                
                scripts = [
                    ("excel_create.py", "1단계: 엑셀 파일 생성"),
                    ("create.py", "2단계: 블로그 본문 생성"),
                ]
                
                for script_name, description in scripts:
                    self.update_status(f"{description} 중...")
                    self.log(f"=== {description} ===")
                    
                    script_path = os.path.join(base_path, script_name)
                    if not os.path.exists(script_path):
                        script_path = script_name
                    
                    python_exe = get_python_executable()
                    process = subprocess.Popen(
                        [python_exe, script_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        cwd=base_path
                    )
                    
                    for line in process.stdout:
                        if line.strip():
                            self.log(line.strip())
                    
                    process.wait()
                    
                    if process.returncode != 0:
                        raise Exception(f"{description} 실패")
                
                if self.schedule_enabled.get():
                    self.log("=== 예약 시간 설정 ===")
                    if not self.update_excel_schedule():
                        raise Exception("예약 시간 설정 실패")
                
                self.update_status("3단계: 블로그 업로드 중...")
                self.log("=== 3단계: 블로그 업로드 ===")
                
                script_path = os.path.join(base_path, "upload_bot.py")
                if not os.path.exists(script_path):
                    script_path = "upload_bot.py"
                
                python_exe = get_python_executable()
                process = subprocess.Popen(
                    [python_exe, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=base_path
                )
                
                for line in process.stdout:
                    if line.strip():
                        self.log(line.strip())
                
                process.wait()
                
                if process.returncode != 0:
                    raise Exception("3단계: 블로그 업로드 실패")
                
                self.update_status("전체 작업 완료")
                self.log("모든 작업이 완료되었습니다!")
                messagebox.showinfo("완료", "모든 작업이 완료되었습니다!")
                
            except Exception as e:
                self.update_status("오류 발생")
                self.log(f"오류: {str(e)}")
                messagebox.showerror("오류", f"오류 발생: {str(e)}")
            finally:
                self.progress_bar.stop()
                self.set_buttons_state(tk.NORMAL)
        
        self.set_buttons_state(tk.DISABLED)
        thread = threading.Thread(target=run_all_scripts, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = BlogAutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
