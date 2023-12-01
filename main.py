from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils.api import getTrending, topAiring, getAnime
import asyncio, httpx

app = FastAPI()

# Configure the 'static' directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

async def fetch_data():
    trending, top = await asyncio.gather(getTrending(), topAiring())

    try:
        trending.sort(key=lambda anime: anime['rating'])
    except Exception as e:
        print(f"Error sorting trending anime: {e}")

    return trending, top

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    trending, top = await fetch_data()

    return templates.TemplateResponse("index.html", {"request": request, "trending": trending, "top": top})

@app.get("/favicon.ico", response_class=HTMLResponse)
async def favicon(request: Request):
    return "static/assets/logo.png"


@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/anime/{anime_id}")
async def anime(request: Request, anime_id: str):
    id = anime_id.split("-")[-1]
    anime = await getAnime(id)
    return templates.TemplateResponse("anime.html", {"request": request, "anime": anime})

@app.get("/watch/{watch_id}")
async def watch(request: Request, watch_id: str):
    id = watch_id.split("-")[-1]

    return templates.TemplateResponse("watch.html", {"request": request, "anime": {'title': "Goblin Slayer"}})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)
