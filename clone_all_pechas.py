import csv
import re
import requests
from pathlib import Path
from git import Repo

config = {
    "OP_ORG": "https://github.com/Openpecha"
}

def get_branch(repo, branch):
    if branch in repo.heads:
        return branch
    return "master"


def download_pecha(pecha_id, out_path=None, branch="master"):
    pecha_url = f"{config['OP_ORG']}/{pecha_id}.git"
    out_path = Path(out_path)
    out_path.mkdir(exist_ok=True, parents=True)
    pecha_path = out_path / pecha_id
    Repo.clone_from(pecha_url, str(pecha_path))
    repo = Repo(str(pecha_path))
    branch_to_pull = get_branch(repo, branch)
    repo.git.checkout(branch_to_pull)
    print(f"{pecha_id} Downloaded ")  

def get_repo_names(headers):
    all_repo_names = []
    for page_num in range(1,200):
        response = requests.get(f"https://api.github.com/orgs/Openpecha/repos?page={page_num}&per_page=100", headers=headers)
        data = response.json()
        for info in data:
            if type(info) is dict:
                repo_name = info["name"]
                all_repo_names.append(repo_name)
    return all_repo_names

if __name__ == "__main__":
    # headers = {"Authorization": f"bearer {token}"}
    # pecha_ids = ""
    # repo_names = get_repo_names(headers)
    repo_names = (Path(f"./repo_names.txt").read_text(encoding='8')).splitlines()
    for repo_name in repo_names:
        output_path = Path(f"./all-openpecha-repos/")
        download_pecha(repo_name, output_path)