import pandas as pd
from collections import OrderedDict
from sklearn.metrics.pairwise import cosine_similarity
from app.utils.settings import Config

def get_recommendation(new_user_ratings, top_n):
    """
    Recommends movies for a new user based on similar users' ratings.

    Parameters:
    - ratings_path (str): Path to the ratings CSV file (e.g., MovieLens dataset).
    - new_user_ratings (dict): A dictionary of {movieId: rating} for the new user.
    - top_n (int): Number of top recommendations to return.

    Returns:
    - pd.Series: Top N recommended movies with their scores.
    """
    # Load the dataset
    ratings = pd.read_csv(Config.RATINGS_PATH)

    # Create the user-movie matrix
    user_movie_matrix = ratings.pivot(index='userId', columns='movieId', values='rating').fillna(0)

    # Add the new user to the matrix
    new_user_id = user_movie_matrix.index.max() + 1
    new_user_row = pd.Series(0, index=user_movie_matrix.columns)
    for movie_id, rating in new_user_ratings.items():
        if movie_id in new_user_row.index:
            new_user_row[movie_id] = rating
    user_movie_matrix = user_movie_matrix._append(new_user_row, ignore_index=True)
    user_movie_matrix.index = list(range(1, len(user_movie_matrix) + 1))

    # Compute the similarity matrix
    similarity_matrix = cosine_similarity(user_movie_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=user_movie_matrix.index, columns=user_movie_matrix.index)

    # Find the most similar users to the new user
    similar_users = similarity_df[new_user_id].sort_values(ascending=False).drop(new_user_id)

    # Compute weighted ratings
    weighted_ratings = pd.Series(0, index=user_movie_matrix.columns)
    for similar_user, similarity_score in similar_users.items():
        user_ratings = user_movie_matrix.loc[similar_user]
        weighted_ratings = weighted_ratings.add(user_ratings * similarity_score, fill_value=0)

    # Normalize weighted ratings
    similarity_sums = similarity_df[new_user_id].sum() - 1
    weighted_ratings = weighted_ratings / similarity_sums

    # Exclude movies already rated by the new user
    recommendations = weighted_ratings[new_user_row == 0]

    # Return the top N recommendations
    return recommendations.sort_values(ascending=False).head(top_n)



def recommend_movies_endpoint(id_items, top_n=10):
    # Creare le valutazioni del nuovo utente utilizzando id_items
    new_user_ratings = {
        id_items[0]: 5,
        id_items[1]: 5,
        id_items[2]: 5,
        id_items[3]: 5,
        id_items[4]: 5
    }

    recommendations = get_recommendation(new_user_ratings, top_n)

    return [{"movieId": movie_id, "score": score} for movie_id, score in recommendations.items()]




