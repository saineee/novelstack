query = """
query ($search: String) {
    Page (perPage: 10) {
    media (search: $search, type: MANGA) {
        id
        title { 
            romaji 
            english 
        }
        coverImage {
        large
    }
    format
}
}
}   
"""

variables = {"search": "Lord of the Mysteries"}

url = "https://graphql.anilist.co"
