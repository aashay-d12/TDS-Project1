import requests
import pandas as pd
import time
import re

GITHUB_TOKEN = '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'
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_users(location="Berlin", min_followers=200):
    url = f"https://api.github.com/search/users?q=location:{location}+followers:>{min_followers}"
    users = []
    response = requests.get(url, headers=headers)
    if response.ok:
        data = response.json().get("items", [])
        for user in data:
            users.append(user['login'])
    return users

def get_user_data(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=headers)
    if response.ok:
        user_data = response.json()
        if user_data.get('company'):
            user_data['company'] = re.sub(r'^\@', '', user_data['company'].strip()).upper()
        return user_data
    return None

def get_repositories(username):
    url = f"https://api.github.com/users/{username}/repos?sort=pushed&per_page=500"
    response = requests.get(url, headers=headers)
    if response.ok:
        repos_data = response.json()
        return repos_data
    return []

def save_to_csv(users, repositories):
    user_rows = []
    for user in users:
        user_rows.append({
            "login": user['login'],
            "name": user.get('name', ''),
            "company": user.get('company', ''),
            "location": user.get('location', ''),
            "email": user.get('email', ''),
            "hireable": user.get('hireable', ''),
            "bio": user.get('bio', ''),
            "public_repos": user.get('public_repos', ''),
            "followers": user.get('followers', ''),
            "following": user.get('following', ''),
            "created_at": user.get('created_at', '')
        })
    users_df = pd.DataFrame(user_rows)
    users_df.to_csv('users.csv', index=False)

    repo_rows = []
    for repo in repositories:
        repo_rows.append({
            "login": repo['owner']['login'],
            "full_name": repo['full_name'],
            "created_at": repo['created_at'],
            "stargazers_count": repo['stargazers_count'],
            "watchers_count": repo['watchers_count'],
            "language": repo.get('language', ''),
            "has_projects": repo.get('has_projects', ''),
            "has_wiki": repo.get('has_wiki', ''),
            "license_name": repo['license']['key'] if repo.get('license') else ''
        })
    repos_df = pd.DataFrame(repo_rows)
    repos_df.to_csv('repositories.csv', index=False)

if __name__ == "__main__":
    users = fetch_users()
    users_data = []
    repositories_data = []
    for username in users:
        user_data = get_user_data(username)
        if user_data:
            users_data.append(user_data)
            repos = get_repositories(username)
            repositories_data.extend(repos)
        time.sleep(1)
    save_to_csv(users_data, repositories_data)
