import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def get_movie_info(title: str, year: Optional[int] = None, include_plot: bool = True,
                   include_ratings: bool = True, include_cast: bool = True):
    """
    Get movie information using OMDB API (Open Movie Database).
    
    Parameters:
    - title (str): Movie title to search for
    - year (int, optional): Release year for more specific search
    - include_plot (bool): Whether to include plot summary
    - include_ratings (bool): Whether to include ratings from various sources
    - include_cast (bool): Whether to include cast information
    
    Returns:
    - dict: Movie information
    """
    try:
        # Validate parameters
        if not title or len(title.strip()) == 0:
            return {"error": "Movie title cannot be empty"}
        
        if year is not None and (year < 1888 or year > 2030):
            return {"error": "Year must be between 1888 and 2030"}
        
        # Get API key from environment (OMDB API key is free)
        api_key = os.getenv('OMDB_API_KEY')
        if not api_key:
            # Use demo key for testing (limited requests)
            api_key = "demo"
        
        # OMDB API endpoint
        base_url = "http://www.omdbapi.com/"
        
        # Build search parameters
        params = {
            "apikey": api_key,
            "t": title.strip(),
            "plot": "full" if include_plot else "short"
        }
        
        if year:
            params["y"] = year
        
        # Make API request
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check for errors
        if data.get("Response") == "False":
            error_msg = data.get("Error", "Unknown error")
            return {"error": f"Movie not found: {error_msg}"}
        
        # Extract movie information
        movie_info = {
            "title": data.get("Title", ""),
            "year": data.get("Year", ""),
            "rated": data.get("Rated", ""),
            "released": data.get("Released", ""),
            "runtime": data.get("Runtime", ""),
            "genre": data.get("Genre", ""),
            "director": data.get("Director", ""),
            "writer": data.get("Writer", ""),
            "plot": data.get("Plot", "") if include_plot else "",
            "language": data.get("Language", ""),
            "country": data.get("Country", ""),
            "awards": data.get("Awards", ""),
            "poster": data.get("Poster", ""),
            "metascore": data.get("Metascore", ""),
            "imdb_rating": data.get("imdbRating", ""),
            "imdb_votes": data.get("imdbVotes", ""),
            "imdb_id": data.get("imdbID", ""),
            "type": data.get("Type", ""),
            "dvd": data.get("DVD", ""),
            "box_office": data.get("BoxOffice", ""),
            "production": data.get("Production", ""),
            "website": data.get("Website", "")
        }
        
        # Parse ratings if requested
        ratings = []
        if include_ratings and data.get("Ratings"):
            for rating in data["Ratings"]:
                ratings.append({
                    "source": rating.get("Source", ""),
                    "value": rating.get("Value", "")
                })
        
        # Parse cast if requested
        cast_list = []
        if include_cast and data.get("Actors"):
            cast_list = [actor.strip() for actor in data["Actors"].split(",")]
        
        # Calculate rating score if available
        rating_score = None
        if movie_info["imdb_rating"] and movie_info["imdb_rating"] != "N/A":
            try:
                rating_score = float(movie_info["imdb_rating"])
            except ValueError:
                pass
        
        # Generate recommendations based on rating
        recommendations = []
        if rating_score:
            if rating_score >= 8.0:
                recommendations.append("Highly recommended - Excellent rating")
            elif rating_score >= 7.0:
                recommendations.append("Recommended - Good rating")
            elif rating_score >= 6.0:
                recommendations.append("Worth watching - Decent rating")
            else:
                recommendations.append("Consider reviews before watching")
        
        # Add genre-based recommendations
        if movie_info["genre"]:
            genres = [g.strip() for g in movie_info["genre"].split(",")]
            if "Action" in genres:
                recommendations.append("Action-packed entertainment")
            if "Comedy" in genres:
                recommendations.append("Good for light entertainment")
            if "Drama" in genres:
                recommendations.append("Emotional and engaging storyline")
            if "Horror" in genres:
                recommendations.append("Suspenseful and thrilling")
            if "Documentary" in genres:
                recommendations.append("Educational and informative")
        
        result = {
            "movie_info": movie_info,
            "ratings": ratings if include_ratings else [],
            "cast": cast_list if include_cast else [],
            "recommendations": recommendations,
            "operation": "get_movie_info",
            "parameters": {
                "title": title,
                "year": year,
                "include_plot": include_plot,
                "include_ratings": include_ratings,
                "include_cast": include_cast
            },
            "success": True
        }
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error getting movie information: {str(e)}"}


if __name__ == "__main__":
    # Example usage
    result = get_movie_info("The Matrix", 1999)
    print(json.dumps(result, indent=2)) 