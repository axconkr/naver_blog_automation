import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import sys
import os
from datetime import datetime

# PyInstaller로 빌드된 경우 실행 파일의 디렉토리 경로 가져오기
def get_base_path():
    """애플리케이션의 기본 경로를 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우
        if sys.platform == 'darwin':
            # macOS: .app 번들 내부
            return os.path.dirname(os.path.dirname(sys.executable))
        else:
            # Windows/Linux: 실행 파일과 같은 디렉토리
            return os.path.dirname(sys.executable)
    else:
        # 개발 환경
        return os.path.dirname(os.path.abspath(__file__))

class BlogAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ 네이버 블로그 자동화 도구")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # 모던한 배경색 (그라데이션 느낌)
        self.root.configure(bg='#f5f7fa')
        
        # 헤더 영역 (그라데이션 느낌)
        header_frame = tk.Frame(root, bg='#667eea', height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # 제목 (헤더에 배치)
        title_label = tk.Label(
            header_frame, 
            text="✨ 네이버 블로그 자동화 도구", 
            font=("Helvetica", 24, "bold"),
            bg='#667eea',
            fg='white'
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="AI 기반 블로그 콘텐츠 자동 생성 및 업로드",
            font=("Helvetica", 11),
            bg='#667eea',
            fg='#e0e7ff'
        )
        subtitle_label.pack(pady=(0, 15))
        
        # 메인 컨테이너
        container = tk.Frame(root, bg='#f5f7fa')
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        self.root.update_idletasks()
        
        # 버튼 영역 (카드 스타일)
        button_card = tk.Frame(container, bg='white', relief=tk.FLAT, bd=0)
        button_card.pack(fill=tk.X, pady=(0, 20))
        
        # 카드 내부 패딩
        button_inner = tk.Frame(button_card, bg='white')
        button_inner.pack(padx=20, pady=20)
        
        # 섹션 제목
        section_title = tk.Label(
            button_inner,
            text="📋 작업 선택",
            font=("Helvetica", 14, "bold"),
            bg='white',
            fg='#2d3748',
            anchor=tk.W
        )
        section_title.pack(fill=tk.X, pady=(0, 15))
        
        # 버튼 그리드
        button_grid = tk.Frame(button_inner, bg='white')
        button_grid.pack(fill=tk.BOTH, expand=True)
        
        # 버튼 스타일 함수
        def create_modern_button(parent, text, icon, color, command):
            btn_frame = tk.Frame(parent, bg='white')
            original_bg = color
            dark_bg = self._darken_color(color)
            
            btn = tk.Button(
                btn_frame,
                text=f"{icon} {text}",
                command=command,
                font=("Helvetica", 12, "bold"),
                bg=original_bg,
                fg='white',
                relief=tk.FLAT,
                bd=0,
                padx=20,
                pady=15,
                cursor='hand2',
                activebackground=dark_bg,
                activeforeground='white'
            )
            
            # 호버 효과
            def on_enter(e):
                btn.config(bg=dark_bg)
            
            def on_leave(e):
                btn.config(bg=original_bg)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            btn.pack(fill=tk.BOTH, expand=True)
            return btn_frame
        
        # 버튼 1: 엑셀 파일 생성
        self.btn_create_excel = create_modern_button(
            button_grid, 
            "엑셀 파일 생성",
            "📊",
            "#10b981",
            self.create_excel
        )
        self.btn_create_excel.grid(row=0, column=0, padx=8, pady=8, sticky='nsew')
        
        # 버튼 2: 블로그 본문 생성
        self.btn_generate_content = create_modern_button(
            button_grid,
            "블로그 본문 생성",
            "✍️",
            "#3b82f6",
            self.generate_content
        )
        self.btn_generate_content.grid(row=0, column=1, padx=8, pady=8, sticky='nsew')
        
        # 버튼 3: 블로그 업로드
        self.btn_upload = create_modern_button(
            button_grid,
            "블로그 업로드",
            "🚀",
            "#f59e0b",
            self.upload_blog
        )
        self.btn_upload.grid(row=1, column=0, padx=8, pady=8, sticky='nsew')
        
        # 버튼 4: 전체 실행
        self.btn_run_all = create_modern_button(
            button_grid,
            "전체 실행",
            "⚡",
            "#8b5cf6",
            self.run_all
        )
        self.btn_run_all.grid(row=1, column=1, padx=8, pady=8, sticky='nsew')
        
        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)
        self.root.update_idletasks()
        
        # 진행 상황 영역 (카드 스타일)
        progress_card = tk.Frame(container, bg='white', relief=tk.FLAT, bd=0)
        progress_card.pack(fill=tk.X, pady=(0, 20))
        
        progress_inner = tk.Frame(progress_card, bg='white')
        progress_inner.pack(padx=20, pady=20)
        
        progress_title = tk.Label(
            progress_inner,
            text="📈 진행 상황",
            font=("Helvetica", 14, "bold"),
            bg='white',
            fg='#2d3748',
            anchor=tk.W
        )
        progress_title.pack(fill=tk.X, pady=(0, 12))
        
        self.progress_var = tk.StringVar(value="⏳ 대기 중...")
        self.progress_label = tk.Label(
            progress_inner, 
            textvariable=self.progress_var, 
            font=("Helvetica", 12),
            bg='white',
            fg='#4a5568',
            anchor=tk.W
        )
        self.progress_label.pack(fill=tk.X, pady=(0, 10))
        self.root.update_idletasks()
        
        # 프로그레스 바 (스타일 개선)
        progress_bar_frame = tk.Frame(progress_inner, bg='white')
        progress_bar_frame.pack(fill=tk.X)
        
        # 프로그레스 바 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Modern.Horizontal.TProgressbar",
                       background='#667eea',
                       troughcolor='#e2e8f0',
                       borderwidth=0,
                       lightcolor='#667eea',
                       darkcolor='#667eea')
        
        self.progress_bar = ttk.Progressbar(
            progress_bar_frame, 
            mode='indeterminate', 
            length=400,
            style='Modern.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X)
        self.root.update_idletasks()
        
        # 로그 출력 영역 (카드 스타일)
        log_card = tk.Frame(container, bg='white', relief=tk.FLAT, bd=0)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        log_inner = tk.Frame(log_card, bg='white')
        log_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        log_title = tk.Label(
            log_inner,
            text="📝 실행 로그",
            font=("Helvetica", 14, "bold"),
            bg='white',
            fg='#2d3748',
            anchor=tk.W
        )
        log_title.pack(fill=tk.X, pady=(0, 12))
        
        self.log_text = scrolledtext.ScrolledText(
            log_inner, 
            height=15, 
            width=70, 
            wrap=tk.WORD, 
            font=("SF Mono", 10),
            bg='#1a202c',
            fg='#e2e8f0',
            relief=tk.FLAT,
            bd=0,
            insertbackground='#60a5fa',
            selectbackground='#3b82f6',
            selectforeground='white',
            padx=15,
            pady=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()
        
        # 상태바 (하단)
        status_frame = tk.Frame(root, bg='#2d3748', height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="✅ 준비됨")
        status_label = tk.Label(
            status_frame, 
            textvariable=self.status_var, 
            anchor=tk.W,
            font=("Helvetica", 10),
            bg='#2d3748',
            fg='#cbd5e0',
            padx=20
        )
        status_label.pack(side=tk.LEFT, fill=tk.Y)
        
        # 버전 정보
        version_label = tk.Label(
            status_frame,
            text="v1.0.0",
            font=("Helvetica", 9),
            bg='#2d3748',
            fg='#718096',
            padx=20
        )
        version_label.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.root.update_idletasks()
        
        # 초기 로그 메시지
        self.log("🎉 GUI 애플리케이션이 시작되었습니다.")
        self.log("💡 위의 버튼을 클릭하여 작업을 시작하세요.")
        
        # 최종 업데이트
        self.root.update()
    
    def _darken_color(self, color):
        """색상을 어둡게 만드는 헬퍼 함수"""
        color_map = {
            "#10b981": "#059669",
            "#3b82f6": "#2563eb",
            "#f59e0b": "#d97706",
            "#8b5cf6": "#7c3aed"
        }
        return color_map.get(color, color)
    
    def _lighten_color(self, color):
        """색상을 밝게 만드는 헬퍼 함수"""
        color_map = {
            "#10b981": "#34d399",
            "#3b82f6": "#60a5fa",
            "#f59e0b": "#fbbf24",
            "#8b5cf6": "#a78bfa"
        }
        return color_map.get(color, color)
        
    def log(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 이모지에 따라 색상 태그 적용
        if "✅" in message or "완료" in message or "성공" in message:
            tag = "success"
        elif "❌" in message or "오류" in message or "실패" in message:
            tag = "error"
        elif "⚠️" in message or "경고" in message:
            tag = "warning"
        elif "ℹ️" in message or "정보" in message:
            tag = "info"
        else:
            tag = "normal"
        
        # 태그 스타일 설정
        self.log_text.tag_config("success", foreground="#10b981")
        self.log_text.tag_config("error", foreground="#ef4444")
        self.log_text.tag_config("warning", foreground="#f59e0b")
        self.log_text.tag_config("info", foreground="#3b82f6")
        self.log_text.tag_config("normal", foreground="#e2e8f0")
        
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, message):
        """상태 업데이트"""
        # 이모지 추가
        if "완료" in message or "성공" in message:
            emoji = "✅"
        elif "실행 중" in message or "처리 중" in message:
            emoji = "⏳"
        elif "오류" in message or "실패" in message:
            emoji = "❌"
        else:
            emoji = "ℹ️"
        
        self.status_var.set(f"{emoji} {message}")
        self.progress_var.set(f"{emoji} {message}")
        self.root.update_idletasks()
        
    def run_script(self, script_name, description):
        """스크립트 실행 (별도 스레드)"""
        def run():
            try:
                self.update_status(f"{description} 실행 중...")
                self.progress_bar.start(10)
                self.log(f"{description} 시작")
                
                # Python 스크립트 실행
                base_path = get_base_path()
                script_path = os.path.join(base_path, script_name)
                
                # 스크립트 파일이 없으면 현재 디렉토리에서 찾기
                if not os.path.exists(script_path):
                    script_path = script_name
                
                # 작업 디렉토리를 base_path로 설정
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=base_path
                )
                
                # 실시간 출력 읽기
                for line in process.stdout:
                    if line.strip():
                        self.log(line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.update_status(f"{description} 완료")
                    self.log(f"✅ {description} 성공적으로 완료되었습니다.")
                    messagebox.showinfo("완료", f"{description}가 완료되었습니다.")
                else:
                    self.update_status(f"{description} 실패")
                    self.log(f"❌ {description} 실행 중 오류가 발생했습니다.")
                    messagebox.showerror("오류", f"{description} 실행 중 오류가 발생했습니다.")
                    
            except Exception as e:
                self.update_status(f"{description} 오류")
                self.log(f"❌ 오류: {str(e)}")
                import traceback
                self.log(f"⚠️ {traceback.format_exc()}")
                messagebox.showerror("오류", f"오류 발생: {str(e)}")
            finally:
                self.progress_bar.stop()
                self.btn_create_excel.config(state=tk.NORMAL)
                self.btn_generate_content.config(state=tk.NORMAL)
                self.btn_upload.config(state=tk.NORMAL)
                self.btn_run_all.config(state=tk.NORMAL)
        
        # 버튼 비활성화
        self.btn_create_excel.config(state=tk.DISABLED)
        self.btn_generate_content.config(state=tk.DISABLED)
        self.btn_upload.config(state=tk.DISABLED)
        self.btn_run_all.config(state=tk.DISABLED)
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
    def create_excel(self):
        """엑셀 파일 생성"""
        self.run_script("excel_create.py", "엑셀 파일 생성")
        
    def generate_content(self):
        """블로그 본문 생성"""
        self.run_script("create.py", "블로그 본문 생성")
        
    def upload_blog(self):
        """블로그 업로드"""
        self.run_script("upload_bot.py", "블로그 업로드")
        
    def run_all(self):
        """전체 실행"""
        def run_all_scripts():
            try:
                self.progress_bar.start(10)
                
                # 1. 엑셀 파일 생성
                self.update_status("1단계: 엑셀 파일 생성 중...")
                self.log("=== 1단계: 엑셀 파일 생성 ===")
                base_path = get_base_path()
                script_path = os.path.join(base_path, "excel_create.py")
                if not os.path.exists(script_path):
                    script_path = "excel_create.py"
                process = subprocess.Popen(
                    [sys.executable, script_path],
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
                    raise Exception("엑셀 파일 생성 실패")
                
                # 2. 블로그 본문 생성
                self.update_status("2단계: 블로그 본문 생성 중...")
                self.log("=== 2단계: 블로그 본문 생성 ===")
                base_path = get_base_path()
                script_path = os.path.join(base_path, "create.py")
                if not os.path.exists(script_path):
                    script_path = "create.py"
                process = subprocess.Popen(
                    [sys.executable, script_path],
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
                    raise Exception("블로그 본문 생성 실패")
                
                # 3. 블로그 업로드
                self.update_status("3단계: 블로그 업로드 중...")
                self.log("=== 3단계: 블로그 업로드 ===")
                base_path = get_base_path()
                script_path = os.path.join(base_path, "upload_bot.py")
                if not os.path.exists(script_path):
                    script_path = "upload_bot.py"
                process = subprocess.Popen(
                    [sys.executable, script_path],
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
                    raise Exception("블로그 업로드 실패")
                
                self.update_status("전체 작업 완료")
                self.progress_bar.stop()
                self.log("✅ 모든 작업이 성공적으로 완료되었습니다!")
                messagebox.showinfo("완료", "🎉 모든 작업이 완료되었습니다!")
                
            except Exception as e:
                self.update_status("오류 발생")
                self.log(f"❌ 오류: {str(e)}")
                import traceback
                self.log(f"⚠️ {traceback.format_exc()}")
                messagebox.showerror("오류", f"오류 발생: {str(e)}")
            finally:
                self.progress_bar.stop()
                self.btn_create_excel.config(state=tk.NORMAL)
                self.btn_generate_content.config(state=tk.NORMAL)
                self.btn_upload.config(state=tk.NORMAL)
                self.btn_run_all.config(state=tk.NORMAL)
        
        # 버튼 비활성화
        self.btn_create_excel.config(state=tk.DISABLED)
        self.btn_generate_content.config(state=tk.DISABLED)
        self.btn_upload.config(state=tk.DISABLED)
        self.btn_run_all.config(state=tk.DISABLED)
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=run_all_scripts, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = BlogAutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
