import requests

def get_random_joke(
    category: list = ["Any"], 
    language: str = "en", 
    flags: list = None, 
    joke_type: list = ["single", "twopart"], 
    search_string: str = None, 
    num_jokes: int = 1
) -> str:
    """
    Fetches a random joke from the JokeAPI based on various filters.

    Parameters:
    - category (list): Defines the joke category. Options include: 'Programming', 'Misc', 'Dark', 'Pun', 'Spooky', 'Christmas', or 'Any'. Defaults to 'Any'.
    - language (str): The language of the joke. Options include: 'cs', 'de', 'en', 'es', 'fr', 'pt'. Defaults to English ('en').
    - flags (list): A list of categories to exclude, such as 'nsfw', 'political', 'racist', 'sexist', 'religious', and 'explicit'. Defaults to None.
    - joke_type (list): Specifies the type of joke. Can be 'single' (one-liner) or 'twopart' (setup and punchline). Defaults to both.
    - search_string (str): Allows filtering the jokes based on a specific string. Defaults to None.
    - num_jokes (int): Specifies how many jokes to fetch. Defaults to 1.

    Returns:
    - str: The joke or an error message.
    """
    
    # Validate Category
    valid_categories = ['Programming', 'Misc', 'Dark', 'Pun', 'Spooky', 'Christmas', 'Any']
    for cat in category:
        if cat not in valid_categories:
            return f"Invalid category: {cat}. Valid categories are: {', '.join(valid_categories)}."

    # Validate Language
    valid_languages = ['cs', 'de', 'en', 'es', 'fr', 'pt']
    if language not in valid_languages:
        return f"Invalid language: {language}. Valid languages are: {', '.join(valid_languages)}."

    # Validate Flags
    valid_flags = ['nsfw', 'political', 'racist', 'sexist', 'religious', 'explicit']
    if flags:
        for flag in flags:
            if flag not in valid_flags:
                return f"Invalid flag: {flag}. Valid flags are: {', '.join(valid_flags)}."

    # Validate Joke Type
    valid_joke_types = ['single', 'twopart']
    for joke in joke_type:
        if joke not in valid_joke_types:
            return f"Invalid joke type: {joke}. Valid joke types are: {', '.join(valid_joke_types)}."

    url = f"https://v2.jokeapi.dev/joke/{','.join(category)}"
    
    params = {
        "lang": language,
        "type": ",".join(joke_type),
        "amount": num_jokes,
    }
    
    if flags:
        params["blacklistFlags"] = ",".join(flags)
    
    if search_string:
        params["contains"] = search_string

    response = requests.get(url, params=params)
    response.raise_for_status()
    joke_data = response.json()
    return joke_data


if __name__ == "__main__":
    # Example usage
    arguments={"category": ["Programming"], "language": "en"}
    # language='en',category=['Programming']
    print(get_random_joke(**arguments))
