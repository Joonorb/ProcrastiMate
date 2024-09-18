from ui import create_ui
from scheduler import run_scheduler
import threading

def main():
    threading.Thread(target=run_scheduler, daemon=True).start()
    create_ui()

if __name__ == "__main__":
    main()
