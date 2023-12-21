from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils.api import getTrending, topAiring, getAnime, getEp, moreAnime, fetch_anime_details_batch, searchAnime
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
    parts = anime_id.split('-')
    title = '-'.join(parts[:-1]).strip()
    q = title
    anime = await getAnime(id)
    return templates.TemplateResponse("anime.html", {"request": request, "anime": anime, "q": q})


async def fetch_watch(title, aniId, target_episode=None):
    async with httpx.AsyncClient() as client:
        anime, ep_data = await asyncio.gather(searchAnime(title, "h"), getEp(title, target_episode))
        
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
    more = None
    try:  
        anime, epi, more = await fetch_watch(title, aniId, ep)
    except Exception as e:
        print(e)
    return templates.TemplateResponse("watch.html", {"request": request, "anime": anime, "more": more, "eps": epi, "title": title})


@app.get("/search")
async def search(request: Request, query: str):
    async with httpx.AsyncClient() as client:
        # print(query)
        resp = await client.get(f"https://consumet-api-phi.vercel.app/anime/zoro/{query.replace("+", " ")}")
        resp.raise_for_status()

        results = resp.json()['results']
        # print(results)
        animes = []
        tasks = []

        for i, anime in enumerate(results):
            shitt = anime['url'].replace("https://aniwatch.to/", " ").replace("?ref=search", "").split("-")
            title = (" ").join(shitt[:-1])
            # print(title)
            task = searchAnime(title, q=anime['title'])
            tasks.append(task)
            if i>8:
                break

        animes = await asyncio.gather(*tasks)
        # for i in animes:
            # print(i['genres'])
    # return animes
    return templates.TemplateResponse("search.html", {"request": request, "results": animes, "q": query})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)