import json
import requests
from app.utils.settings import Config
from app.utils.llm_adapter import ResponseAdapter


def llm_query(rated_movies, movie_to_recommend):

    system_prompt = """
        You are being configured as a movie recommendation system. Your task will be to analyze a user's movie preferences based on the ratings they have given to a series of films. Using this information, you will craft a persuasive text that justifies the recommendation of a specific movie, aiming to convince the user to watch it.

        Here’s how you will proceed:
        1. Analyze User Preferences: Evaluate the information provided on the user’s previous movie ratings to identify trends and specific tastes.
        2. Craft a Persuasive Argument: Write a text that persuades the user to watch the suggested movie, leveraging the tastes previously expressed by the user. Use engaging language and logically justify the movie choice.

        Final Goal: Create a movie recommendation that is not only relevant but also persuasive enough to motivate the user to watch the suggested film.
        """

    recommendation_prompt = f"""
    **Task: Movie Recommendation**

    Objective: Based on the user's provided ratings, write a persuasive text that convinces the user to watch a specific movie.

    User Data:
    - **Rated Movies**:
    {rated_movies}
    - **Movie to Recommend**: {movie_to_recommend}

    Details:
    1. **Analyze the Ratings**: Identify the user’s preferences based on the provided ratings.
    2. **Create a Persuasive Text**: Write a text that justifies the choice of the recommended movie, leveraging the user’s tastes and using engaging language.
       - **Introduction**: Acknowledge the user’s preferences.
       - **Argumentation**: Describe how the recommended movie reflects or enhances the elements the user appreciated in previous films.
       - **Conclusion**: Invite the user to watch the movie, highlighting the main reasons why they would find it engaging.
    """

    headers = {'Content-Type': 'application/json'}

    if Config.LLM_ENDPOINT_TYPE == 'openrouter':

        url = Config.LLM_URL
        headers["Authorization"] = f"Bearer {Config.OPENROUTER_KEY}"

        data = {
            "model": Config.LLM_MODEL,
            "temperature": 0.5,
            "messages": [
                {"system": f"{system_prompt}"},
                {"role": f"{recommendation_prompt}"}
            ]
        }

    elif Config.LLM_ENDPOINT_TYPE == 'ollama':

        url = Config.LLM_URL

        data = {
            "model": Config.LLM_MODEL,
            "temperature": Config.LLM_TEMPERATURE,
            "messages": [
                {
                    "role": "user",
                    "content": f"{system_prompt}\n{recommendation_prompt}",
                }
            ],
            "stream": False
        }

    else:
        raise ValueError("Invalid LLM_ENDPOINT_TYPE. Please set it to 'openrouter' or 'ollama'.")

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return ResponseAdapter(response.json(), Config.LLM_ENDPOINT_TYPE).to_dict()
    else:
        print(f"Error: {response.status_code}, {response.text}")


def test_llm():
    return llm_query("breaking bad", "the godfather")