from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils.api import getTrending, topAiring, getAnime, getEp, moreAnime, fetch_anime_details_batch
import asyncio, httpx

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

async def fetch_data():
    async with httpx.AsyncClient() as client:
        trending, top = await asyncio.gather(getTrending(), topAiring())
        try:
            trending.sort(key=lambda anime: anime['rating'])
        except Exception as e:
            print(f"Error sorting trending anime: {e}")

        titles = [anime['title'] for anime in trending[:3]]
        image_urls = await fetch_anime_details_batch(client, titles)

        for anime, image_url in zip(trending[:3], image_urls):
            anime['image'] = image_url

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


async def fetch_watch(title, aniId, target_episode=None):
    async with httpx.AsyncClient() as client:
        anime, ep_data = await asyncio.gather(getAnime(aniId), getEp(title, target_episode))
        
        more = await moreAnime(anime['genres'], client)

    return anime, ep_data, more

@app.get("/watch/{watch_id}")
async def watch(request: Request, watch_id: str):

    ids = watch_id.split("-")[-1]
    aniId = ids.split('$')[0]
    ep = ids.split('$')[1]
    
    parts = watch_id.split('-')
    title = '-'.join(parts[:-1]).strip()
    title = title.replace("-", " ")

    # print(await getEp(title, ep))
    anime = None
    try:  
        anime, epi, more = await fetch_watch(title, aniId, ep)
        # print(epi)
    except Exception as e:
        print(e)
    return templates.TemplateResponse("watch.html", {"request": request, "anime": anime, "more": more, "eps": epi})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)