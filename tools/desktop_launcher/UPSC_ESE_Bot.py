import os
import sys
import subprocess
import threading
import webbrowser
import socket
import time
import tkinter as tk
from tkinter import ttk, scrolledtext

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 5000
APP_URL = f"http://127.0.0.1:{PORT}"


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


class UPSCESELocalBot:
    def __init__(self, root):
        self.root = root
        self.root.title("UPSC ESE (Mechanical) — Local AI Exam Bot")
        self.root.geometry("680x560")
        self.root.configure(bg="#0f172a")
        self.process = None

        # Header
        header = tk.Frame(root, bg="#1e293b", pady=14, padx=20)
        header.pack(fill=tk.X)

        title_lbl = tk.Label(
            header,
            text="⚙️ UPSC ESE (Mechanical Engineering) — Local AI Hub",
            font=("Segoe UI", 14, "bold"),
            fg="#f8fafc",
            bg="#1e293b"
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            header,
            text="100% Local on your PC • Zero Cloud Storage Costs • OpenAI Powered",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#1e293b"
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Status Bar
        status_frame = tk.Frame(root, bg="#0f172a", pady=10, padx=20)
        status_frame.pack(fill=tk.X)

        self.status_dot = tk.Label(status_frame, text="●", font=("Segoe UI", 14), fg="#ef4444", bg="#0f172a")
        self.status_dot.pack(side=tk.LEFT)

        self.status_text = tk.Label(
            status_frame,
            text="Server Stopped",
            font=("Segoe UI", 11, "bold"),
            fg="#e2e8f0",
            bg="#0f172a"
        )
        self.status_text.pack(side=tk.LEFT, padx=(6, 15))

        self.url_label = tk.Label(
            status_frame,
            text=APP_URL,
            font=("Consolas", 10, "underline"),
            fg="#38bdf8",
            bg="#0f172a",
            cursor="hand2"
        )
        self.url_label.pack(side=tk.RIGHT)
        self.url_label.bind("<Button-1>", lambda e: webbrowser.open(APP_URL))

        # Control Buttons
        btn_frame = tk.Frame(root, bg="#0f172a", padx=20, pady=5)
        btn_frame.pack(fill=tk.X)

        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Start Local Server",
            font=("Segoe UI", 10, "bold"),
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.start_server
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = tk.Button(
            btn_frame,
            text="■ Stop Server",
            font=("Segoe UI", 10, "bold"),
            bg="#ef4444",
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.stop_server
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.open_admin_btn = tk.Button(
            btn_frame,
            text="🌐 Open App in Browser",
            font=("Segoe UI", 10, "bold"),
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            command=lambda: webbrowser.open(f"{APP_URL}/login")
        )
        self.open_admin_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.open_ai_btn = tk.Button(
            btn_frame,
            text="✨ Open AI Assistant",
            font=("Segoe UI", 10, "bold"),
            bg="#8b5cf6",
            fg="white",
            activebackground="#7c3aed",
            activeforeground="white",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            command=lambda: webbrowser.open(f"{APP_URL}/learn-with-ai")
        )
        self.open_ai_btn.pack(side=tk.LEFT)

        # Credentials Box
        cred_frame = tk.LabelFrame(
            root,
            text=" 🔑 Local Login Accounts (Password for both: saibaba123) ",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
            bd=1,
            padx=12,
            pady=8
        )
        cred_frame.pack(fill=tk.X, padx=20, pady=12)

        admin_row = tk.Frame(cred_frame, bg="#1e293b")
        admin_row.pack(fill=tk.X, pady=2)
        tk.Label(
            admin_row,
            text="Admin (Create Questions / AI Generator / Mock Tests):  admin@openlms.dev  |  Pass: Admin@123",
            font=("Consolas", 9),
            fg="#f8fafc",
            bg="#1e293b"
        ).pack(side=tk.LEFT)
        tk.Button(
            admin_row,
            text="Copy Email",
            font=("Segoe UI", 8),
            bg="#334155",
            fg="white",
            relief=tk.FLAT,
            command=lambda: self.copy_text("admin@openlms.dev")
        ).pack(side=tk.RIGHT)

        stu_row = tk.Frame(cred_frame, bg="#1e293b")
        stu_row.pack(fill=tk.X, pady=2)
        tk.Label(
            stu_row,
            text="Student (Take Mock Tests / Practice / AI Tutor):       student@upsc.local  |  Pass: saibaba123",
            font=("Consolas", 9),
            fg="#38bdf8",
            bg="#1e293b"
        ).pack(side=tk.LEFT)
        tk.Button(
            stu_row,
            text="Copy Email",
            font=("Segoe UI", 8),
            bg="#334155",
            fg="white",
            relief=tk.FLAT,
            command=lambda: self.copy_text("student@upsc.local")
        ).pack(side=tk.RIGHT)

        # Log Console
        log_frame = tk.Frame(root, bg="#0f172a", padx=20)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        tk.Label(
            log_frame,
            text="Live Server Logs:",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#0f172a"
        ).pack(anchor="w", pady=(0, 4))

        self.log_box = scrolledtext.ScrolledText(
            log_frame,
            bg="#020617",
            fg="#cbd5e1",
            font=("Consolas", 9),
            insertbackground="white",
            relief=tk.FLAT
        )
        self.log_box.pack(fill=tk.BOTH, expand=True)

        self.log("Ready! Click '▶ Start Local Server' to launch your UPSC ESE Mechanical AI platform.")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Auto-start server on launch
        self.root.after(400, self.start_server)

    def copy_text(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log(f"Copied to clipboard: {text}")

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_box.see(tk.END)

    def find_python(self):
        if os.path.exists(r"C:\Python313\python.exe"):
            return r"C:\Python313\python.exe"
        return sys.executable

    def start_server(self):
        if self.process and self.process.poll() is None:
            self.log("Server is already running.")
            return

        py_exe = self.find_python()
        self.log(f"Starting UPSC ESE Local Server on {APP_URL} using {py_exe}...")

        env = os.environ.copy()
        env["FLASK_APP"] = "wsgi.py"
        env["FLASK_ENV"] = "development"
        env["PYTHONUNBUFFERED"] = "1"

        run_code = (
            "from wsgi import app; "
            f"app.run(host='127.0.0.1', port={PORT}, debug=False, use_reloader=False)"
        )

        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        self.process = subprocess.Popen(
            [py_exe, "-c", run_code],
            cwd=BACKEND_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=creationflags
        )

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_dot.config(fg="#10b981")
        self.status_text.config(text=f"Server Running on {APP_URL}")

        threading.Thread(target=self.stream_logs, daemon=True).start()
        threading.Thread(target=self.wait_and_open_browser, daemon=True).start()

    def wait_and_open_browser(self):
        for _ in range(30):
            if is_port_in_use(PORT):
                self.log("Server is live! Opening browser...")
                webbrowser.open(f"{APP_URL}/login")
                return
            time.sleep(0.5)

    def stream_logs(self):
        if not self.process or not self.process.stdout:
            return
        for line in iter(self.process.stdout.readline, ''):
            if line:
                self.root.after(0, self.log, line.rstrip())
        self.root.after(0, self.on_server_stopped)

    def on_server_stopped(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_dot.config(fg="#ef4444")
        self.status_text.config(text="Server Stopped")

    def stop_server(self):
        if self.process and self.process.poll() is None:
            self.log("Stopping server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.log("Server stopped.")
        self.on_server_stopped()

    def on_close(self):
        self.stop_server()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = UPSCESELocalBot(root)
    root.mainloop()
