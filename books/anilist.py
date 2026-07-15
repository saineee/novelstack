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