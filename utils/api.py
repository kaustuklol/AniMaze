import httpx
import asyncio

trendingApi = "https://consumet-api-phi.vercel.app/meta/anilist/trending?perPage=10"
topAiringApi = "https://graphql.anilist.co"

async def getTrending():
    async with httpx.AsyncClient() as client:
        query = """
            query {
            Page(page: 1, perPage: 10) {
                media(sort: TRENDING_DESC, type: ANIME) {
                id
                title {
                    romaji
                    english
                }
                coverImage {
                    large
                }
                format
                averageScore
                startDate {
                    year
                    month
                    day
                }
                description
                genres
                status
                bannerImage
                }
                
            }
            }
            """

        response = await client.post(topAiringApi, json={"query": query})
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()

            # Extract relevant information
            top_trending_anime = []
            for anime in data["data"]["Page"]["media"]:
                anime_info = {
                    "id": anime["id"],
                    "title": {'romaji': anime["title"]["romaji"], 'english': anime["title"]["english"]},
                    "cover": anime["bannerImage"],
                    "type": anime["format"],
                    "rating": anime["averageScore"],
                    "releaseDate": f"{anime['startDate']['year']}-{anime['startDate']['month']}-{anime['startDate']['day']}",
                    "description": anime["description"],
                    "genres": anime["genres"],
                    "status": anime["status"],
                }
                top_trending_anime.append(anime_info)
    return top_trending_anime

async def topAiring():
    topAiringQuery = """
    query ($status: MediaStatus) {
      Page(page: 1, perPage: 100) {
        media(status: $status, sort: POPULARITY_DESC) {
          id
          title {
            romaji
            english
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
                title = anime['title']['english']
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

            # Use asyncio.gather to concurrently process anime
            await asyncio.gather(*(process_anime(anime) for anime in top_anime))

        # Sort the list by rating in descending order and return only the top 10
        result.sort(key=lambda x: float(x['rating']) if x['rating'] != "N/A" else 0, reverse=True)
        return result[:10]

async def process_anime(anime, result, client):
    title = anime['title']['romaji']
    season = anime['season'] or "N/A"

    if anime['status'] == "RELEASING" and not anime.get('isAdult', False) and season != "N/A":
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
        "search": anime_name,
        "type": "ANIME"
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
                await process_anime(anime, result, client)

        return result

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
            averageScore
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
                    'id': anime_id,
                    'title': anime_data['title']['english'],
                    'jap': anime_data['title']['native'],
                    'status': anime_data['status'],
                    'rating': anime_data['averageScore'] or "N/A",
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

async def getImg(client, title):
    try:
        resp = await client.get(f"https://consumet-api-phi.vercel.app/anime/zoro/{title}")
        resp.raise_for_status()
        image_url = resp.json()['results'][0]['image']
    except Exception as e:
        image_url = "N/A"
    return image_url

async def fetch_anime_details_batch(client, titles):
    tasks = [getImg(client, title) for title in titles]
    return await asyncio.gather(*tasks)

async def moreAnime(genres, client):
    url = "https://graphql.anilist.co"
    query = '''
    query ($genres: [String]) {
        Page {
            media (genre_in: $genres, type: ANIME, sort: POPULARITY_DESC) {
                id
                title {
                    english
                    romaji
                }
                averageScore
                genres
                coverImage {
                    medium
                    large
                }
            }
        }
    }
    '''
    variables = {"genres": genres}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    response = await client.post(url, json={"query": query, "variables": variables}, headers=headers)
    response.raise_for_status()
    data = response.json()
    anime_list = data.get("data", {}).get("Page", {}).get("media", [])

    result = []
    max_title_length = 25

    # Create a list of tasks for fetching anime details concurrently
    tasks = [getImg(client, anime["title"]["english"] or anime["title"]["romaji"]) for anime in anime_list[:3]]
    image_urls = await asyncio.gather(*tasks)

    for anime, image_url in zip(anime_list[:3], image_urls):
        id = anime['id']
        english_title = anime["title"]["english"]
        romaji_title = anime["title"]["romaji"]
        title = english_title if english_title else romaji_title
        average_score = anime["averageScore"]
        genres = anime["genres"]

        # Check the length of the title and add "..." if it exceeds the maximum length
        truncated_title = title[:max_title_length] + ("..." if len(title) > max_title_length else "")

        result.append({"id": id, "title": truncated_title, "rating": average_score, "genres": genres, "poster": image_url})

    return result

async def epiData(client, base_url, anime_id, episode_id, type):
    try:
        url = f"{base_url}watch?episodeId={episode_id.replace('$both', f'${type}')}"
        resp = await client.get(url)
        resp.raise_for_status()

        sources = resp.json()['sources']
        subtitles = resp.json()['subtitles']

        # Extracting all subtitle URLs and languages
        subtitle_data = []
        for subtitle in subtitles:
            subtitle_data.append({'url': subtitle['url'], 'lang': subtitle['lang']})

        return {type: sources[1]['url'], f'{type}titles': subtitle_data}

    except Exception as e:
        print(e)
        return {type: None, f'{type}titles': None}


async def fetchSpecificEpisode(client, base_url, anime_id, episodes, target_episode):
    # Find the data for the targeted episode
    target_episode_data = None
    for epi in episodes:
        if int(epi['number']) == int(target_episode):
            episode_id = epi['id']
            sub_data = await epiData(client, base_url, anime_id, episode_id, 'sub')
            dub_data = await epiData(client, base_url, anime_id, episode_id, 'dub')

            target_episode_data = {
                'number': epi['number'],
                'title': epi['title'],
                **sub_data,
                **dub_data
            }
            break

    return target_episode_data

async def getEp(name, target_episode):
    base_url = 'https://consumet-api-phi.vercel.app/anime/zoro/'

    async with httpx.AsyncClient() as client:
        anime_url = f'{base_url}{name}'
        anime_response = await client.get(anime_url)

        anime_response.raise_for_status()
        for i, anime in enumerate(anime_response.json()['results']):
            if anime['title'].lower() == name.lower(): 
                anime_id = anime_response.json()['results'][i]['id']

        episode_url = f"{base_url}info?id={anime_id}"

        episode_response = await client.get(episode_url)
        episode_response.raise_for_status()
        episodes = episode_response.json()['episodes']

        eps = []
        for epi in episodes:
            ep = {"number": epi['number'], "title": epi['title']}
            eps.append(ep)
            

        # Fetch only the targeted episode
        target_episode_data = await fetchSpecificEpisode(client, base_url, anime_id, episodes, target_episode)


    return target_episode_data, eps


# async def main():
#     print(await searchAnime("bleach thousand year blood war arc"))

# asyncio.run(main())