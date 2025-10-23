import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def get_music_info(query: str = "", search_type: str = "track", 
                   limit: int = 5, output_path: Optional[str] = None):
    """
    Get music information using Last.fm API.
    
    Parameters:
    - query (str): Search query (artist, track, or album name)
    - search_type (str): Type of search ("track", "artist", "album")
    - limit (int): Number of results to return (1-50)
    - output_path (str, optional): Path to save music information
    
    Returns:
    - dict: Music information including details, tags, similar artists, etc.
    """
    try:
        # Validate parameters
        if not query or len(query.strip()) == 0:
            return {"error": "Query cannot be empty"}
        
        if search_type not in ["track", "artist", "album"]:
            return {"error": "Search type must be 'track', 'artist', or 'album'"}
        
        if limit < 1 or limit > 50:
            return {"error": "Limit must be between 1 and 50"}
        
        # Last.fm API (free tier available)
        api_key = os.getenv('LASTFM_API_KEY')
        
        base_url = "http://ws.audioscrobbler.com/2.0/"
        
        # Build API request
        if search_type == "track":
            method = "track.search"
            params = {
                "method": method,
                "track": query,
                "api_key": api_key,
                "format": "json",
                "limit": limit
            }
        elif search_type == "artist":
            method = "artist.search"
            params = {
                "method": method,
                "artist": query,
                "api_key": api_key,
                "format": "json",
                "limit": limit
            }
        else:  # album
            method = "album.search"
            params = {
                "method": method,
                "album": query,
                "api_key": api_key,
                "format": "json",
                "limit": limit
            }
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract results based on search type
        if search_type == "track":
            results = data.get("results", {}).get("trackmatches", {}).get("track", [])
            if not isinstance(results, list):
                results = [results] if results else []
        elif search_type == "artist":
            results = data.get("results", {}).get("artistmatches", {}).get("artist", [])
            if not isinstance(results, list):
                results = [results] if results else []
        else:  # album
            results = data.get("results", {}).get("albummatches", {}).get("album", [])
            if not isinstance(results, list):
                results = [results] if results else []
        
        # Process results
        processed_results = []
        for item in results[:limit]:
            if search_type == "track":
                processed_item = {
                    "name": item.get("name", ""),
                    "artist": item.get("artist", ""),
                    "url": item.get("url", ""),
                    "listeners": item.get("listeners", "0"),
                    "image": item.get("image", []),
                    "mbid": item.get("mbid", "")
                }
            elif search_type == "artist":
                processed_item = {
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "listeners": item.get("listeners", "0"),
                    "image": item.get("image", []),
                    "mbid": item.get("mbid", ""),
                    "streamable": item.get("streamable", "")
                }
            else:  # album
                processed_item = {
                    "name": item.get("name", ""),
                    "artist": item.get("artist", ""),
                    "url": item.get("url", ""),
                    "image": item.get("image", []),
                    "mbid": item.get("mbid", "")
                }
            
            processed_results.append(processed_item)
        
        # Get detailed information for the first result
        detailed_info = {}
        if processed_results and api_key != "demo_key":
            try:
                first_result = processed_results[0]
                if search_type == "track":
                    # Get track info
                    track_params = {
                        "method": "track.getInfo",
                        "track": first_result["name"],
                        "artist": first_result["artist"],
                        "api_key": api_key,
                        "format": "json"
                    }
                    track_response = requests.get(base_url, params=track_params, timeout=10)
                    if track_response.status_code == 200:
                        track_data = track_response.json().get("track", {})
                        detailed_info = {
                            "album": track_data.get("album", {}).get("title", ""),
                            "duration": track_data.get("duration", ""),
                            "playcount": track_data.get("playcount", ""),
                            "listeners": track_data.get("listeners", ""),
                            "tags": [tag.get("name", "") for tag in track_data.get("toptags", {}).get("tag", [])],
                            "wiki": track_data.get("wiki", {}).get("summary", "")[:500] + "..." if len(track_data.get("wiki", {}).get("summary", "")) > 500 else track_data.get("wiki", {}).get("summary", "")
                        }
                
                elif search_type == "artist":
                    # Get artist info
                    artist_params = {
                        "method": "artist.getInfo",
                        "artist": first_result["name"],
                        "api_key": api_key,
                        "format": "json"
                    }
                    artist_response = requests.get(base_url, params=artist_params, timeout=10)
                    if artist_response.status_code == 200:
                        artist_data = artist_response.json().get("artist", {})
                        detailed_info = {
                            "bio": artist_data.get("bio", {}).get("summary", "")[:500] + "..." if len(artist_data.get("bio", {}).get("summary", "")) > 500 else artist_data.get("bio", {}).get("summary", ""),
                            "tags": [tag.get("name", "") for tag in artist_data.get("tags", {}).get("tag", [])],
                            "similar_artists": [artist.get("name", "") for artist in artist_data.get("similar", {}).get("artist", [])[:5]],
                            "stats": {
                                "listeners": artist_data.get("stats", {}).get("listeners", ""),
                                "playcount": artist_data.get("stats", {}).get("playcount", "")
                            }
                        }
                
                else:  # album
                    # Get album info
                    album_params = {
                        "method": "album.getInfo",
                        "album": first_result["name"],
                        "artist": first_result["artist"],
                        "api_key": api_key,
                        "format": "json"
                    }
                    album_response = requests.get(base_url, params=album_params, timeout=10)
                    if album_response.status_code == 200:
                        album_data = album_response.json().get("album", {})
                        detailed_info = {
                            "tracks": [track.get("name", "") for track in album_data.get("tracks", {}).get("track", [])],
                            "tags": [tag.get("name", "") for tag in album_data.get("tags", {}).get("tag", [])],
                            "wiki": album_data.get("wiki", {}).get("summary", "")[:500] + "..." if len(album_data.get("wiki", {}).get("summary", "")) > 500 else album_data.get("wiki", {}).get("summary", ""),
                            "listeners": album_data.get("listeners", ""),
                            "playcount": album_data.get("playcount", "")
                        }
            
            except Exception as e:
                print(f"Warning: Could not fetch detailed information: {e}")
        
        result = {
            "success": True,
            "search_query": query,
            "search_type": search_type,
            "results_count": len(processed_results),
            "results": processed_results,
            "detailed_info": detailed_info,
        }
        
        # Save to file if output_path is provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                result["output_path"] = output_path
            except Exception as e:
                print(f"Warning: Could not save to file: {e}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error getting music info: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = get_music_info_from_lastfm("Bohemian Rhapsody", "track", 3)
    print(json.dumps(result, indent=2)) 