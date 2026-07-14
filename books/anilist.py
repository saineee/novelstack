import logging
import requests

logger = logging.getLogger("novelstack")


query = """
query ($search: String) {
    Page (perPage: 10) {
    media (search: $search, type: MANGA) {
        id
        title { 
            romaji 
            english 
        }
        description
        chapters
        startDate {
            year
            month
            day
        }
        format
        countryOfOrigin
        genres
        status
        coverImage {
            large
        }
        staff {
            edges {
                role
                node {
                    name {
                        full
                    }
                }
            }
        }  
        }
    }
}   
"""

url = "https://graphql.anilist.co"

def fetch_candidates(title):
    variables = {"search": title}
    logger.debug("searching AniList for %s", title)
    response = requests.post(url, json={'query': query, 'variables': variables})
    return response.json()



def extract_candidates(response):
    cleaned_data = []
    candidates = response['data']['Page']['media']
    for candidate in candidates:
        title_data = candidate.get('title', {})
        eng_title = title_data.get('english')
        rom_title = title_data.get('romaji')

        cleaned = {
            'id': candidate.get('id', None),
            'anilist_cover_url': candidate.get('coverImage', {}).get('large', None),
            'format': candidate.get('format', None),
            'title': eng_title if eng_title else rom_title
        }

        cleaned_data.append(cleaned)
    return cleaned_data