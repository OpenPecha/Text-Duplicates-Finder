from cmath import e
import csv
from lib2to3.pgen2 import token
import re
import requests
from pathlib import Path
from git import Repo
import logging
import os


github_token = os.environ.get("GITHUB_TOKEN")

config = {
    "OP_ORG": f"https://{github_token}:x-oauth-basic@github.com/OpenPecha-Data"
}

formatter = logging.Formatter('%(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def notifier(logger,msg):
    logger.info(msg)
def get_branch(repo, branch):
    if branch in repo.heads:
        return branch
    return "main"

def git_push(PATH_OF_GIT_REPO,COMMIT_MESSAGE,files):
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add(files)
        repo.index.commit(COMMIT_MESSAGE)
        origin = repo.remote(name='origin')
        origin.push()
    except Exception as e:
        print(e) 

def download_pecha(pecha_id, out_path=None, branch="master"):
    logger = setup_logger("error_repos","error_repos.log")
    pecha_url = f"{config['OP_ORG']}/{pecha_id}.git"
    out_path = Path(out_path)
    out_path.mkdir(exist_ok=True, parents=True)
    pecha_path = out_path / pecha_id
    Repo.clone_from(pecha_url, str(pecha_path))
    repo = Repo(str(pecha_path))
    branch_to_pull = get_branch(repo, branch)
    try:
        repo.git.checkout(branch_to_pull)
    except:
        notifier(logger,f"{pecha_id} has problem")
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
    output_path = Path(f"/mnt/d/")
    repo_names = (Path(f"./repo_names.txt").read_text(encoding='utf-8')).splitlines()
    for num, repo_name in enumerate(repo_names, 1):
        if num > 7982:
            download_pecha(repo_name, output_path)