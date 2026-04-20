#!/usr/bin/env python3
"""
LottoAI Project Launcher - GUI Interface
ทำให้ใช้งานโปรเจคง่าย ไม่ต้องใช้ Command Line

วิธีใช้:
  python launcher.py
  หรือ ดับเบิลคลิก launcher.py (ต้องติดตั้ง Python ก่อน)
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# ตรวจสอบ Python Version
if sys.version_info < (3, 8):
    print("❌ ต้อง Python 3.8+ ขึ้นไป")
    sys.exit(1)

# ลองนำเข้า tkinter (GUI Library)
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
    print("⚠️  tkinter ไม่พบ - ใช้ Console Mode แทน")


class LottoAILauncher:
    """GUI Launcher สำหรับ LottoAI"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎲 LottoAI Project Launcher")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # ตั้งค่า Theme
        style = ttk.Style()
        style.theme_use('clam')

        # Colors
        self.bg_color = "#1a1a2e"
        self.fg_color = "#ffffff"
        self.accent_color = "#4f46e5"

        self.root.configure(bg=self.bg_color)

        # State
        self.server_running = False
        self.server_process = None

        # สร้าง UI
        self.create_ui()

        # ตรวจสอบ Setup
        self.check_setup()

    def create_ui(self):
        """สร้าง User Interface"""

        # Header
        header = tk.Frame(self.root, bg=self.accent_color, height=60)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="🎲 LottoAI Project Launcher",
            font=("Arial", 16, "bold"),
            bg=self.accent_color,
            fg=self.fg_color
        )
        title.pack(pady=15)

        # Main Frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="📊 สถานะ", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 15))

        self.status_text = tk.Label(
            status_frame,
            text="กำลังตรวจสอบ...",
            font=("Arial", 10),
            fg="#999",
            bg=self.bg_color,
            justify=tk.LEFT
        )
        self.status_text.pack(anchor=tk.W)

        # Server Status
        self.server_status = tk.Label(
            status_frame,
            text="🔴 Server ปิด",
            font=("Arial", 11, "bold"),
            fg="#ef4444",
            bg=self.bg_color
        )
        self.server_status.pack(anchor=tk.W, pady=(10, 0))

        # Buttons Frame
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=15)

        # Start Button
        self.start_btn = tk.Button(
            button_frame,
            text="🚀 รัน Server",
            command=self.start_server,
            font=("Arial", 11, "bold"),
            bg="#10b981",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Stop Button
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ ปิด Server",
            command=self.stop_server,
            font=("Arial", 11, "bold"),
            bg="#ef4444",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Info Frame
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ ข้อมูล", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=15)

        info_text = scrolledtext.ScrolledText(
            info_frame,
            height=10,
            font=("Courier", 9),
            bg="#0f172a",
            fg="#94a3b8",
            relief=tk.FLAT
        )
        info_text.pack(fill=tk.BOTH, expand=True)

        info_content = """🎯 วิธีใช้งาน:

1. คลิก "🚀 รัน Server" เพื่อเริ่มโปรเจค
2. รอ 10-15 วินาที จนเห็น "✅ Server รันอยู่"
3. เปิดเบราว์เซอร์ไปที่: http://localhost:8000
4. เบิ่งพัฒนา LottoAI Dashboard
5. คลิก "⏹️ ปิด Server" เพื่อปิด

📍 URLs:
  Main: http://localhost:8000
  Admin: http://localhost:8000/admin

💡 Tips:
  • ตรวจสอบสถานะ ด้านบน
  • ถ้ามีปัญหา อ่าน RUN_PROJECT_GUIDE_TH.md
"""
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)

        self.info_text = info_text

        # Footer
        footer = tk.Frame(self.root, bg="#0f172a", height=30)
        footer.pack(fill=tk.X)

        footer_label = tk.Label(
            footer,
            text="ติดตั้งดำเนินการโดย LottoAI | © 2026",
            font=("Arial", 8),
            bg="#0f172a",
            fg="#64748b"
        )
        footer_label.pack(pady=5)

    def check_setup(self):
        """ตรวจสอบการติดตั้ง"""
        checks = self.run_checks()
        self.update_status(checks)

    def run_checks(self):
        """รันการตรวจสอบ"""
        results = []

        # ตรวจสอบ Python
        results.append(("Python", sys.version.split()[0], "✓"))

        # ตรวจสอบ Project DIR
        project_dir = Path(__file__).parent
        if project_dir.exists():
            results.append(("Project Directory", str(project_dir), "✓"))
        else:
            results.append(("Project Directory", "ไม่พบ", "✗"))

        # ตรวจสอบ venv
        venv_dir = project_dir / "venv"
        if venv_dir.exists():
            results.append(("Virtual Environment", "ติดตั้งแล้ว", "✓"))
        else:
            results.append(("Virtual Environment", "ยังไม่สร้าง", "⚠️"))

        # ตรวจสอบ Database
        db_file = project_dir / "db.sqlite3"
        if db_file.exists():
            results.append(("Database", "ติดตั้งแล้ว", "✓"))
        else:
            results.append(("Database", "ยังไม่สร้าง", "⚠️"))

        return results

    def update_status(self, checks):
        """อัปเดตสถานะ"""
        status_lines = []
        for check_name, check_value, check_status in checks:
            status_lines.append(f"{check_status} {check_name}: {check_value}")

        self.status_text.config(text="\n".join(status_lines))

    def start_server(self):
        """รัน Server"""
        if self.server_running:
            messagebox.showwarning("แจ้งเตือน", "Server กำลังรันอยู่แล้ว")
            return

        self.update_info("🚀 กำลังเริ่ม Server...\n")

        # รัน Server ใน Background
        def run():
            try:
                project_dir = Path(__file__).parent

                # สร้าง Virtual Environment ถ้ายังไม่มี
                venv_dir = project_dir / "venv"
                if not venv_dir.exists():
                    self.update_info("⚙️ สร้าง Virtual Environment...\n")
                    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

                # ติดตั้ง Requirements ถ้ายังไม่มี
                self.update_info("📦 ตรวจสอบ Dependencies...\n")

                # Migrate ถ้ายังไม่มี Database
                db_file = project_dir / "db.sqlite3"
                if not db_file.exists():
                    self.update_info("🗄️ สร้างฐานข้อมูล...\n")
                    # รัน migrate (ต้องเข้า venv ก่อน)

                # รัน Django Server
                self.update_info("✅ Server รันอยู่!\n")
                self.update_info("🌐 ไปที่: http://localhost:8000\n")

                self.server_running = True
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                self.server_status.config(
                    text="🟢 Server รันอยู่",
                    fg="#10b981"
                )

                # รัน runserver
                python_exe = venv_dir / ("Scripts\\python.exe" if sys.platform == "win32" else "bin/python")
                if not python_exe.exists():
                    python_exe = sys.executable

                os.chdir(str(project_dir))
                self.server_process = subprocess.Popen(
                    [str(python_exe), "manage.py", "runserver"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                # อ่าน Output
                for line in self.server_process.stdout:
                    if line:
                        self.update_info(line)

            except Exception as e:
                self.update_info(f"❌ Error: {str(e)}\n")
                messagebox.showerror("Error", f"ล้มเหลว: {str(e)}")
                self.server_running = False
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.server_status.config(
                    text="🔴 Server ปิด",
                    fg="#ef4444"
                )

        # รันใน Thread
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def stop_server(self):
        """ปิด Server"""
        if not self.server_running:
            messagebox.showwarning("แจ้งเตือน", "Server ไม่ได้รันอยู่")
            return

        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)

            self.server_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.server_status.config(
                text="🔴 Server ปิด",
                fg="#ef4444"
            )
            self.update_info("✅ Server ปิดแล้ว\n")
            messagebox.showinfo("สำเร็จ", "Server ปิดสำเร็จ")

        except Exception as e:
            messagebox.showerror("Error", f"ล้มเหลว: {str(e)}")

    def update_info(self, text):
        """อัปเดต Info Text"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, text)
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
        self.root.update()


class ConsoleLauncher:
    """Console Mode สำหรับผู้ที่ไม่มี tkinter"""

    def __init__(self):
        self.server_running = False
        self.server_process = None

    def run(self):
        """รัน Console Menu"""
        print("\n" + "="*50)
        print("   🎲 LottoAI Project Launcher")
        print("="*50 + "\n")

        while True:
            print("\n📋 เมนู:")
            print("  1. 🚀 รัน Server")
            print("  2. ⏹️ ปิด Server")
            print("  3. 📊 ตรวจสอบสถานะ")
            print("  4. ❌ ออก")
            print()

            choice = input("เลือก (1-4): ").strip()

            if choice == "1":
                self.start_server()
            elif choice == "2":
                self.stop_server()
            elif choice == "3":
                self.check_status()
            elif choice == "4":
                print("\n✅ ปิดแล้ว")
                break
            else:
                print("❌ ตัวเลือกไม่ถูกต้อง")

    def start_server(self):
        """เริ่ม Server"""
        if self.server_running:
            print("⚠️ Server กำลังรันอยู่แล้ว")
            return

        print("\n🚀 กำลังเริ่ม Server...\n")

        try:
            project_dir = Path(__file__).parent
            os.chdir(str(project_dir))

            # รัน runserver
            self.server_process = subprocess.Popen(
                [sys.executable, "manage.py", "runserver"]
            )

            self.server_running = True
            print("✅ Server รันที่: http://localhost:8000")
            print("📌 ปิด Server: เลือกตัวเลือก 2\n")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def stop_server(self):
        """ปิด Server"""
        if not self.server_running:
            print("⚠️ Server ไม่ได้รันอยู่")
            return

        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)

            self.server_running = False
            print("✅ Server ปิดแล้ว\n")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def check_status(self):
        """ตรวจสอบสถานะ"""
        print("\n📊 สถานะ:")
        print(f"  Python: {sys.version.split()[0]}")
        print(f"  Server: {'🟢 รันอยู่' if self.server_running else '🔴 ปิด'}")

        project_dir = Path(__file__).parent
        print(f"  Project: {project_dir}")
        print(f"  venv: {'✓ มี' if (project_dir / 'venv').exists() else '✗ ไม่มี'}")
        print(f"  Database: {'✓ มี' if (project_dir / 'db.sqlite3').exists() else '✗ ไม่มี'}\n")


def main():
    """Main Entry Point"""

    if HAS_TKINTER:
        # รัน GUI
        root = tk.Tk()
        app = LottoAILauncher(root)
        root.mainloop()
    else:
        # รัน Console
        launcher = ConsoleLauncher()
        launcher.run()


if __name__ == "__main__":
    main()
