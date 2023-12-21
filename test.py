import httpx
topAiringApi = "https://graphql.anilist.co"
async def process_anime(anime, result, client):
    title = anime['title']['romaji']
    season = anime['season'] or "N/A"

    if season != "N/A":
        id = anime['id']
        rating = anime['averageScore'] or "N/A"
        status = anime['status'] or "N/A"
        episodes = anime['episodes'] or "N/A"
        genres = anime['genres'] or []
        synopsis = anime['description'] or "N/A"
        try:
            resp = await client.get(f"https://consumet-api-phi.vercel.app/anime/zoro/{title}")
            resp.raise_for_status()
            image_url = resp.json()['results'][0]['image']
        except Exception as e:
            image_url = anime['coverImage']['large'] if anime.get('coverImage') else "N/A"

        result.append({
            "id": id,
            "title": title,
            "status": status,
            "rating": rating,
            "episodes": episodes,
            "season": season,
            "genres": genres,
            "synopsis": synopsis,
            "image": image_url
        })

    return result


async def searchAnime(anime_name):
    searchQuery = """
    query ($search: String, $type: MediaType) {
      Page(page: 1, perPage: 10) {
        media(search: $search, type: $type) {
          id
          title {
            romaji
          }
          status
          averageScore
          isAdult
          episodes
          season
          genres
          description
          coverImage {
            large
          }
        }
      }
    }
    """

    variables = {
        "search": anime_name
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(topAiringApi, json={"query": searchQuery, "variables": variables})
        response.raise_for_status()

        result = []

        if response.status_code == 200:
            data = response.json()
            anime_list = data.get("data", {}).get("Page", {}).get("media", [])


            if not anime_list:
                print(f"No data available for anime with name '{anime_name}'.")
                return result

            for anime in anime_list:
                result = await process_anime(anime, result, client)

        return result

async def main():
    print(await searchAnime("attack on titan"))

import asyncio
asyncio.run(main())
