from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.responses import HTMLResponse
from pathlib import Path
import os
import re

import illness_schedule

app = FastAPI()

ARTICLE_RE = re.compile(r"^(?:[1-9]\d{0,2})$")  # 1..999
ILLNESS_SCHEDULE_DIR = Path(os.getenv("ILLNESS_SCHEDULE_DIR")).resolve()

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Hello World"

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/article/{number}", response_class=HTMLResponse)
async def article(number: str) -> str:
    try:
        result = illness_schedule.get_article_text(number, ILLNESS_SCHEDULE_DIR)
        return f"""
        <a href="{result.url}">Article link</a>
        <pre>{result.text}</pre>
        """
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Article not found")
