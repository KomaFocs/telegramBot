from datetime import datetime

def time_log(message: str) -> None:
    print(f"[{datetime.now():%d/%m/%Y - %H:%M:%S}]: {message}")