import httpx, asyncio
from utils.util import refresh

trendingApi = "https://consumet-api-phi.vercel.app/meta/anilist/trending?perPage=10"
topAiringApi = "https://graphql.anilist.co"



async def getTrending():
    async with httpx.AsyncClient() as client:
        response = await client.get(trendingApi)
        response.raise_for_status()
        data = response.json()
        return data['results']


async def topAiring():
    topAiringQuery = """
    query ($status: MediaStatus) {
      Page(page: 1, perPage: 100) {
        media(status: $status, sort: POPULARITY_DESC) {
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
        "status": "RELEASING"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(topAiringApi, json={"query": topAiringQuery, "variables": variables})
        response.raise_for_status()

        result = []
        seen_titles = set()

        if response.status_code == 200:
            data = response.json()
            top_anime = data.get("data", {}).get("Page", {}).get("media", [])

            if not top_anime:
                print("No data available for top airing anime.")
                return result

            async def process_anime(anime):
                title = anime['title']['romaji']
                season = anime['season'] or "N/A"

                if anime['status'] == "RELEASING" and not anime.get('isAdult', False) and season != "N/A":
                    if title not in seen_titles:
                        seen_titles.add(title)
                        id =  anime['id']
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
                            "title": title,
                            "status": status,
                            "rating": rating,
                            "episodes": episodes,
                            "season": season,
                            "genres": genres,
                            "synopsis": synopsis,
                            "image": image_url
                        })

            # Use asyncio.gather to concurrently process anime
            await asyncio.gather(*(process_anime(anime) for anime in top_anime))

        # Sort the list by rating in descending order and return only the top 10
        result.sort(key=lambda x: float(x['rating']) if x['rating'] != "N/A" else 0, reverse=True)
        return result[:10]


async def getAnime(anime_id):
    url = 'https://graphql.anilist.co'

    query = '''
    query ($animeId: Int) {
        Media(id: $animeId, type: ANIME) {
            title {
                english
                romaji
                native
            }
            status
            episodes
            duration
            studios {
                edges {
                    isMain
                    node {
                        name
                    }
                }
            }
            averageScore
            genres
            description
            coverImage {
                medium
                large
            }
            bannerImage
        }
    }
    '''


    variables = {
        'animeId': anime_id
    }

    headers = {
        'Content-Type': 'application/json',
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={'query': query, 'variables': variables}, headers=headers)

        if response.status_code == 200:
            data = response.json()
            anime_data = data.get('data', {}).get('Media')
            if anime_data:
                details = {
                    'title': anime_data['title']['english'],
                    'jap': anime_data['title']['native'],
                    'status': anime_data['status'],
                    'episodes': anime_data['episodes'],
                    'duration': anime_data['duration'],
                    'poster': anime_data['coverImage']['large'],
                    'banner': anime_data['bannerImage'],
                }

                # Extract the name of the main studio (if available)
                main_studio_name = None
                for studio in anime_data['studios']['edges']:
                    if studio['isMain']:
                        main_studio_name = studio['node']['name']
                        break

                details['studio'] = main_studio_name if main_studio_name else 'Not available'

                details['score'] = anime_data['averageScore']
                details['genres'] = anime_data['genres']
                details['synopsis'] = anime_data['description']

                return details
            else:
                print('Anime not found.')
        else:
            print(f'Error: {response.status_code}')

# async def main():
#     top_airing_anime = await topAiring()

#     for index, anime in enumerate(top_airing_anime, start=1):
#         print(f"{index}. {anime['title']} - Status: {anime['status']}, Rating: {anime['rating']}, Episodes: {anime['episodes']}, Season: {anime['season']}")
#         print(f"   Genres: {', '.join(anime['genres'])}")
#         print(f"   Synopsis: {anime['synopsis']}")
#         print(f"   Image: {anime['image']}")
#         print()

# asyncio.run(main())
