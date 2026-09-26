import os
import sys
import threading
import time
import socket
import webview
from waitress import serve

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS
    WORKING_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    WORKING_DIR = BUNDLE_DIR

sys.path.insert(0, BUNDLE_DIR)
os.chdir(WORKING_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.management import call_command

def run_migrations():
    try:
        call_command('migrate', interactive=False)
    except Exception as e:
        print(f"Migration check: {e}")

def run_server():
    from config.wsgi import application
    serve(application, host='127.0.0.1', port=8000, threads=4, _quiet=True)

def main():
    run_migrations()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    time.sleep(1.0)
    
    window = webview.create_window(
        "Siraj UPS & Solar — Billing & Inventory Software",
        "http://127.0.0.1:8000",
        width=1300,
        height=850,
        resizable=True,
        min_size=(1024, 700)
    )
    
    webview.start()

if __name__ == '__main__':
    main()
