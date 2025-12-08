from fastapi import FastAPI
import time
from rct_core import unix_to_rct_ns, anchor

app = FastAPI()

@app.get("/rct/now")
def rct_now():
    unix_now = time.time()
    rct_now_ns = unix_to_rct_ns(unix_now, anchor)
    return {
        "rct_ns": rct_now_ns,
        "unix_ts": unix_now,
        "anchor": anchor.name
    }
