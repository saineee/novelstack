import logging
import requests
from requests import RequestException

logger = logging.getLogger("novelstack")

MEDIA_FIELDS = """
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
        """

SEARCH_QUERY = """
query ($search: String) {
    Page (perPage: 10) {
    media (search: $search, type: MANGA) {
 """ + MEDIA_FIELDS + """       
        }
    }
}   
"""

ID_QUERY = """
query ($id: Int) {
    Media (id: $id) {
""" + MEDIA_FIELDS + """    
    }
}
"""
url = "https://graphql.anilist.co"


def fetch_candidates(title):
    variables = {"search": title}
    logger.debug("searching AniList for %s", title)
    try:
        response = requests.post(url, json={'query': SEARCH_QUERY, 'variables': variables}, timeout=10)
    except RequestException as e:
        logger.exception("AniList request failed: %s,", e)
        return None
    data = response.json()
    if data.get('errors'):
        logger.error("AniList returned errors: %s", data.get('errors'))
        return None
    else:
        return data

def fetch_id(anilist_id):
    variables = {"id": anilist_id}
    logger.debug("searching AniList for %s", anilist_id)
    try:
        response = requests.post(url, json={'query': ID_QUERY, 'variables': variables}, timeout=10)
    except RequestException as e:
        logger.e("AniList request failed: %s,", e)
        return None
    data = response.json()
    if data.get('errors'):
        logger.error("AniList returned errors: %s", data.get('errors'))
        return None
    else:
        return data