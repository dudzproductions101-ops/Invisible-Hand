import logging

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log(message: str):
    logging.info(message)

def show_logs() -> str:
    try:
        with open("logs.txt", "r") as f:
            content = f.read()
            return content if content else "Log file is empty."
    except FileNotFoundError:
        return "Log file not found."
