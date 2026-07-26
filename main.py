# main.py

import os
import time
import json
import threading

import logs
import ui
import stress

STOP_EVENT = threading.Event()
PAUSE_EVENT = threading.Event()

NUM_THREADS = 5
REQUEST_DELAY = 0.0
SMART_MODE = True

logo = r"""
████████╗██╗  ██╗███████╗    ██╗███╗   ██╗██╗   ██╗██╗███████╗██╗██████╗ ██╗     ███████╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ 
╚══██╔══╝██║  ██║██╔════╝    ██║████╗  ██║██║   ██║██║██╔════╝██║██╔══██╗██║     ██╔════╝    ██║  ██║██╔══██╗████╗  ██║██╔══██╗
   ██║   ███████║█████╗      ██║██╔██╗ ██║██║   ██║██║███████╗██║██████╔╝██║     █████╗      ███████║███████║██╔██╗ ██║██║  ██║
   ██║   ██╔══██║██╔══╝      ██║██║╚██╗██║╚██╗ ██╔╝██║╚════██║██║██╔══██╗██║     ██╔══╝      ██╔══██║██╔══██║██║╚██╗██║██║  ██║
   ██║   ██║  ██║███████╗    ██║██║ ╚████║ ╚████╔╝ ██║███████║██║██████╔╝███████╗███████╗    ██║  ██║██║  ██║██║ ╚████║██████╔╝
   ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝╚══════╝╚═╝╚═════╝ ╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ 
"""


def load_config():
    global NUM_THREADS, REQUEST_DELAY, SMART_MODE
    if not os.path.exists("config.json"):
        return
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
        NUM_THREADS = cfg.get("default_threads", NUM_THREADS)
        REQUEST_DELAY = cfg.get("default_delay", REQUEST_DELAY)
        SMART_MODE = cfg.get("smart_mode_default", SMART_MODE)
    except Exception as e:
        logs.log(f"Error loading config.json: {e}", level="warning")


def validate_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def input_listener():
    while True:
        key = input().strip().lower()
        if key == "q":
            STOP_EVENT.set()
            logs.log("User aborted the stress test.")
            break
        elif key == "p":
            PAUSE_EVENT.set()
            logs.log("Stress test paused.")
        elif key == "r":
            PAUSE_EVENT.clear()
            logs.log("Stress test resumed.")


def print_stats(stats, total_time):
    print("\n=== PERFORMANCE STATS ===")
    print(f"Total time: {total_time:.3f}s")
    print(f"Total requests: {stats['total']}")
    print(f"Errors: {stats['errors']}")
    print(f"Timeouts: {stats['timeouts']}")
    if stats["times"]:
        avg = sum(stats["times"]) / len(stats["times"])
        rps = stats["total"] / total_time if total_time > 0 else 0
        print(f"Average response time: {avg:.3f}s")
        print(f"Fastest: {stats['fastest']:.3f}s")
        print(f"Slowest: {stats['slowest']:.3f}s")
        print(f"Requests per second (approx): {rps:.2f} req/s")
    else:
        print("No timing data recorded.")
    print("Status codes:")
    for code, count in stats["codes"].items():
        print(f"  {code}: {count}")


def settings_menu():
    global NUM_THREADS, REQUEST_DELAY, SMART_MODE
    while True:
        print("\n=== SETTINGS (v7.4) ===")
        print(f"1. Threads (current: {NUM_THREADS})")
        print(f"2. Delay between requests (current: {REQUEST_DELAY}s)")
        print(f"3. Smart Stress v2 (current: {'ON' if SMART_MODE else 'OFF'})")
        print("4. Back")
        choice = input("Choose an option (1-4): ")
        if choice == "1":
            try:
                value = int(input("Enter number of threads: "))
                if value > 0:
                    NUM_THREADS = value
                else:
                    print("Threads must be > 0.")
            except ValueError:
                print("Invalid number.")
        elif choice == "2":
            try:
                value = float(input("Enter delay in seconds (e.g. 0.0): "))
                if value >= 0:
                    REQUEST_DELAY = value
                else:
                    print("Delay must be >= 0.")
            except ValueError:
                print("Invalid number.")
        elif choice == "3":
            SMART_MODE = not SMART_MODE
            print(f"Smart Stress v2 is now {'ON' if SMART_MODE else 'OFF'}.")
        elif choice == "4":
            break
        else:
            print("Invalid option.")


def main():
    load_config()
    ui.clear_screen()
    print(logo)
    print("\nInvisible Hand v7.4 — Maximum Speed Edition")
    print("--------------------------------------------------------------------------\n")
    while True:
        print("Select an Option")
        print("1. Start Stress Test")
        print("2. Show Logs")
        print("3. Clear Logs")
        print("4. Settings")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")
        if choice == "1":
            url = input("Enter URL: ")
            if not validate_url(url):
                print("Invalid URL. Must start with http:// or https://")
                continue
            STOP_EVENT.clear()
            PAUSE_EVENT.clear()
            stats = {
                "total": 0,
                "errors": 0,
                "timeouts": 0,
                "codes": {},
                "times": [],
                "fastest": float("inf"),
                "slowest": 0.0,
            }
            listener = threading.Thread(target=input_listener, daemon=True)
            listener.start()
            start_time = time.time()
            threads = stress.run_stress(
                url,
                NUM_THREADS,
                REQUEST_DELAY,
                SMART_MODE,
                stats,
                STOP_EVENT,
                PAUSE_EVENT
            )
            while any(t.is_alive() for t in threads) and not STOP_EVENT.is_set():
                active = sum(1 for t in threads if t.is_alive())
                ui.dashboard(stats, active, NUM_THREADS, SMART_MODE, logo)
                time.sleep(0.05)
            for t in threads:
                t.join()
            total_time = time.time() - start_time
            ui.clear_screen()
            print(logo)
            print_stats(stats, total_time)
        elif choice == "2":
            print("\n=== LOGS ===")
            print(logs.show_logs())
        elif choice == "3":
            print(logs.clear_logs())
        elif choice == "4":
            settings_menu()
        elif choice == "5":
            print("Exiting Invisible Hand v7.4...")
            break
        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    main()
