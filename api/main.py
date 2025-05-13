from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.routers import generator
from api.core.config import settings
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Question Generator API")

BASE_DIR = Path(__file__).resolve().parent
# Mount static files and templates
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Include routers
app.include_router(generator.router)

@app.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.get('/favicon.ico', include_in_schema=False)
# async def favicon():
#     return FileResponse('app/static/favicon.ico')