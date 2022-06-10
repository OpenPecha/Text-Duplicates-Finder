import csv
import re
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


if __name__ == "__main__":
    output_path = Path(f"./all-openpecha-pechas/")
    with open("catalog.csv", newline="") as csvfile:
        pechas = list(csv.reader(csvfile, delimiter=","))
        for pecha in pechas[0:]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            download_pecha(pecha_id, output_path)