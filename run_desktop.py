import os
import sys
import time
import urllib.request
import subprocess
import socket

PORT = 8000
URL = f"http://127.0.0.1:{PORT}"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = os.path.join(PROJECT_DIR, "venv", "Scripts", "python.exe")
MANAGE_PY = os.path.join(PROJECT_DIR, "manage.py")

def is_server_running():
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=1):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def start_django_server():
    if not is_server_running():
        # Start Django server in background
        cmd = [PYTHON_EXE, MANAGE_PY, "runserver", f"127.0.0.1:{PORT}", "--noreload"]
        proc = subprocess.Popen(
            cmd,
            cwd=PROJECT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        # Wait until server responds
        for _ in range(30):
            if is_server_running():
                break
            time.sleep(0.5)
        return proc
    return None

def launch_window():
    server_proc = start_django_server()
    
    launched = False
    try:
        import webview
        window = webview.create_window(
            "Siraj UPS & Solar — Billing & Inventory Management",
            URL,
            width=1300,
            height=850,
            resizable=True,
            min_size=(1024, 700)
        )
        webview.start()
        launched = True
    except Exception as e:
        print(f"pywebview startup fallback: {e}")

    if not launched:
        # Fallback to Edge/Chrome in --app mode (standalone desktop window format)
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        
        browser_exe = None
        for path in edge_paths + chrome_paths:
            if os.path.exists(path):
                browser_exe = path
                break
        
        if browser_exe:
            proc = subprocess.Popen([browser_exe, f"--app={URL}", "--window-size=1300,850"])
            proc.wait()
        else:
            import webbrowser
            webbrowser.open(URL)

    # Clean up Django server on window exit if we spawned it
    if server_proc:
        try:
            server_proc.terminate()
            server_proc.wait(timeout=2)
        except Exception:
            try:
                server_proc.kill()
            except Exception:
                pass

if __name__ == "__main__":
    launch_window()
