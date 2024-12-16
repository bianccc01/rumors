import ast
import re
from typing import List, Optional

from flask import current_app, jsonify
from pydantic import BaseModel
from pymongo import ASCENDING
from pymongo.errors import OperationFailure
from requests import get, exceptions


def get_movie_poster(image_id):
    return "https://image.tmdb.org/t/p/w500" + image_id

def get_movie_genres(genres):
    # Ensure that `genres` is a list of dictionaries. If it's a string, convert it to a list.
    if isinstance(genres, str):
        genres = ast.literal_eval(genres)

    # Check if `genres` is a list and each item is a dictionary with a 'name' key
    if isinstance(genres, list) and all(isinstance(genre, dict) and 'name' in genre for genre in genres):
        return " | ".join([genre['name'] for genre in genres])
    else:
        return ""

def fetch_movie_info(movie_id):
    language = 'en-US'
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language={language}&external_source=imdb_id"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + current_app.config['TMDB_API_KEY']
    }

    try:
        response = get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except (exceptions.HTTPError, KeyError, Exception) as e:
        current_app.logger.error(f"Error fetching movie info: {e}")
        RuntimeError(f"Error fetching movie info: {e}")
        return None


def search_items(query, sort='title', limit=10, page=1):
    limit = min(int(limit), 100)
    page = max(int(page), 1)
    sort = sort if sort in ['title', 'imdbId', 'match'] else 'match'
    db = current_app.db

    # Define the search filter and projection
    search_filter = {}
    projection = {}

    if query:
        tokens = query.split()
        if tokens:
            # Create a regex pattern with lookaheads for each token
            query_pattern = '.*' + '.*'.join(re.escape(token) for token in tokens) + '.*'
        else:
            query_pattern = '.*'

        # Use MongoDB text search if index exists on 'title'
        if 'title_text' in db.list_collection_names():  # Example condition, adapt as needed
            search_filter['$text'] = {'$search': {
                "index": "title",
                "autocomplete": {
                    "query": query,
                    "path": "title",
                }
            }}
            projection['score'] = {'$meta': 'textScore'}
        else:
            search_filter = {'title': {'$regex': query_pattern, '$options': 'i'}}
            projection = {}  # No score available for regex searches

    # Pagination setup
    skip = (page - 1) * limit

    try:
        # Determine the sort field
        if sort == 'match' and 'score' in projection:
            sort_field = [('score', {'$meta': 'textScore'})]
        else:
            sort_field = [(sort, ASCENDING)]

        # Execute the search query
        items_cursor = (db.items
                        .find(search_filter, projection)
                        .sort(sort_field)
                        .skip(skip)
                        .limit(limit))
        items = list(items_cursor)

        # Process items
        for item in items:
            item['_id'] = str(item['_id'])
            item['poster_path'] = get_movie_poster(item.get('poster_path'))
            item['genres'] = get_movie_genres(item.get('genres'))

        return items

    except OperationFailure as e:
        raise RuntimeError(f"Database operation failed: {str(e)}")

    except Exception as e:
        raise RuntimeError(f"An error occurred during search: {str(e)}")


class Movie(BaseModel):
    title: str
    genres: List[str] = []
    overview: Optional[str] = None
    release_date: Optional[str] = None
    poster_path: Optional[str] = None
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None
    movielens_id: Optional[str] = None
