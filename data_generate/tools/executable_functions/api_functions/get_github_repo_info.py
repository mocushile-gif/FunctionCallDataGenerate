import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def get_github_repo_info(owner: str, repo: str, include_details: bool = True,
                        output_path: Optional[str] = None):
    """
    Get comprehensive GitHub repository information.
    
    Parameters:
    - owner (str): Repository owner/organization name
    - repo (str): Repository name
    - include_details (bool): Whether to include detailed information
    - output_path (str, optional): Path to save repository information
    
    Returns:
    - dict: Repository information including stats, languages, contributors, etc.
    """
    try:
        # Validate parameters
        if not owner or len(owner.strip()) == 0:
            return {"error": "Owner cannot be empty"}
        
        if not repo or len(repo.strip()) == 0:
            return {"error": "Repository name cannot be empty"}
        
        # GitHub API base URL
        base_url = "https://api.github.com"
        
        # Get basic repository information
        repo_url = f"{base_url}/repos/{owner}/{repo}"
        
        # Use GitHub token if available for higher rate limits
        headers = {}
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        response = requests.get(repo_url, headers=headers, timeout=10)
        response.raise_for_status()
        repo_data = response.json()
        
        # Extract basic information
        basic_info = {
            "name": repo_data.get("name", repo),
            "full_name": repo_data.get("full_name", f"{owner}/{repo}"),
            "description": repo_data.get("description", ""),
            "homepage": repo_data.get("homepage", ""),
            "html_url": repo_data.get("html_url", ""),
            "clone_url": repo_data.get("clone_url", ""),
            "ssh_url": repo_data.get("ssh_url", ""),
            "git_url": repo_data.get("git_url", ""),
            "svn_url": repo_data.get("svn_url", ""),
            "mirror_url": repo_data.get("mirror_url", ""),
            "language": repo_data.get("language", ""),
            "default_branch": repo_data.get("default_branch", "main"),
            "license": repo_data.get("license", {}),
            "topics": repo_data.get("topics", []),
            "visibility": repo_data.get("visibility", ""),
            "private": repo_data.get("private", False),
            "fork": repo_data.get("fork", False),
            "archived": repo_data.get("archived", False),
            "disabled": repo_data.get("disabled", False),
            "template": repo_data.get("template", False),
            "allow_forking": repo_data.get("allow_forking", True),
            "web_commit_signoff_required": repo_data.get("web_commit_signoff_required", False),
            "has_discussions": repo_data.get("has_discussions", False),
            "has_downloads": repo_data.get("has_downloads", True),
            "has_issues": repo_data.get("has_issues", True),
            "has_pages": repo_data.get("has_pages", False),
            "has_projects": repo_data.get("has_projects", True),
            "has_wiki": repo_data.get("has_wiki", True),
            "has_sponsors": repo_data.get("has_sponsors", False),
            "is_template": repo_data.get("is_template", False),
            "open_issues_count": repo_data.get("open_issues_count", 0),
            "open_issues": repo_data.get("open_issues", 0),
            "watchers": repo_data.get("watchers", 0),
            "watchers_count": repo_data.get("watchers_count", 0),
            "forks": repo_data.get("forks", 0),
            "forks_count": repo_data.get("forks_count", 0),
            "stargazers_count": repo_data.get("stargazers_count", 0),
            "subscribers_count": repo_data.get("subscribers_count", 0),
            "network_count": repo_data.get("network_count", 0),
            "size": repo_data.get("size", 0),
            "created_at": repo_data.get("created_at", ""),
            "updated_at": repo_data.get("updated_at", ""),
            "pushed_at": repo_data.get("pushed_at", ""),
            "owner": {
                "login": repo_data.get("owner", {}).get("login", owner),
                "id": repo_data.get("owner", {}).get("id", 0),
                "type": repo_data.get("owner", {}).get("type", ""),
                "avatar_url": repo_data.get("owner", {}).get("avatar_url", ""),
                "html_url": repo_data.get("owner", {}).get("html_url", "")
            }
        }
        
        # Get additional details if requested
        detailed_info = {}
        if include_details:
            try:
                # Get languages
                languages_url = f"{base_url}/repos/{owner}/{repo}/languages"
                languages_response = requests.get(languages_url, headers=headers, timeout=10)
                if languages_response.status_code == 200:
                    detailed_info["languages"] = languages_response.json()
                
                # Get contributors (limited to first 10)
                contributors_url = f"{base_url}/repos/{owner}/{repo}/contributors?per_page=10"
                contributors_response = requests.get(contributors_url, headers=headers, timeout=10)
                if contributors_response.status_code == 200:
                    contributors_data = contributors_response.json()
                    detailed_info["contributors"] = [
                        {
                            "login": c.get("login", ""),
                            "id": c.get("id", 0),
                            "contributions": c.get("contributions", 0),
                            "avatar_url": c.get("avatar_url", ""),
                            "html_url": c.get("html_url", "")
                        }
                        for c in contributors_data
                    ]
                
                # Get releases (latest)
                releases_url = f"{base_url}/repos/{owner}/{repo}/releases?per_page=5"
                releases_response = requests.get(releases_url, headers=headers, timeout=10)
                if releases_response.status_code == 200:
                    releases_data = releases_response.json()
                    detailed_info["releases"] = [
                        {
                            "tag_name": r.get("tag_name", ""),
                            "name": r.get("name", ""),
                            "body": r.get("body", "")[:200] + "..." if len(r.get("body", "")) > 200 else r.get("body", ""),
                            "created_at": r.get("created_at", ""),
                            "published_at": r.get("published_at", ""),
                            "prerelease": r.get("prerelease", False),
                            "draft": r.get("draft", False)
                        }
                        for r in releases_data
                    ]
                
                # Get README content
                readme_url = f"{base_url}/repos/{owner}/{repo}/readme"
                readme_response = requests.get(readme_url, headers=headers, timeout=10)
                if readme_response.status_code == 200:
                    readme_data = readme_response.json()
                    import base64
                    readme_content = base64.b64decode(readme_data.get("content", "")).decode('utf-8')
                    detailed_info["readme"] = {
                        "content": readme_content[:500] + "..." if len(readme_content) > 500 else readme_content,
                        "encoding": readme_data.get("encoding", ""),
                        "size": readme_data.get("size", 0)
                    }
                
            except Exception as e:
                print(f"Warning: Could not fetch some detailed information: {e}")
        
        # Calculate repository age
        from datetime import datetime
        try:
            created_date = datetime.fromisoformat(basic_info["created_at"].replace("Z", "+00:00"))
            updated_date = datetime.fromisoformat(basic_info["updated_at"].replace("Z", "+00:00"))
            current_date = datetime.now(created_date.tzinfo)
            
            age_days = (current_date - created_date).days
            last_activity_days = (current_date - updated_date).days
            
            basic_info["age_days"] = age_days
            basic_info["last_activity_days"] = last_activity_days
        except:
            basic_info["age_days"] = None
            basic_info["last_activity_days"] = None
        
        # Format size
        size_kb = basic_info["size"]
        if size_kb > 1024:
            size_mb = size_kb / 1024
            basic_info["size_formatted"] = f"{size_mb:.1f} MB"
        else:
            basic_info["size_formatted"] = f"{size_kb} KB"
        
        result = {
            "repository_info": basic_info,
            "detailed_info": detailed_info if include_details else {},
            "operation": "get_github_repo_info",
            "parameters": {
                "owner": owner,
                "repo": repo,
                "include_details": include_details
            },
            "success": True
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
        return {"error": f"Error getting GitHub repository info: {str(e)}"}


if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = get_github_repo_info("microsoft", "vscode")
    print(json.dumps(result, indent=2)) 