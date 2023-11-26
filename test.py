# from AnilistPython import Anilist

# anilist = Anilist()

# print(anilist.get_anime("jujutsu kaisen season 2"))

import requests

def get_anime_info_by_id(anime_id):
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
        }
    }
    '''

    variables = {
        'animeId': anime_id
    }

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        anime_data = data.get('data', {}).get('Media')
        if anime_data:
            return anime_data
        else:
            print('Anime not found.')
    else:
        print(f'Error: {response.status_code}')

anime_id_to_lookup = 154587
anime_info = get_anime_info_by_id(anime_id_to_lookup)

if anime_info:
    print('Title:', anime_info['title']['english'])
    print('Status:', anime_info['status'])
    print('Episodes:', anime_info['episodes'])
    
    # Extract the name of the main studio (if available)
    main_studio_name = None
    for studio in anime_info['studios']['edges']:
        if studio['isMain']:
            main_studio_name = studio['node']['name']
            break

    print('Main Studio:', main_studio_name if main_studio_name else 'Not available')
    
    print('Average Score:', anime_info['averageScore'])
    print('Genres:', anime_info['genres'])
    print('Synopsis:', anime_info['description'])
