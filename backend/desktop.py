import os
import threading
import time
import urllib.request

import uvicorn

from app.main import app


def open_browser() -> None:
    url = "http://127.0.0.1:8000"
    health_url = f"{url}/api/health"
    for _ in range(40):
        try:
            with urllib.request.urlopen(health_url, timeout=0.5):
                os.startfile(url)
                return
        except Exception:
            time.sleep(0.25)


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
