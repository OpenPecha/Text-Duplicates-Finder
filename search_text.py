from opf_search_sequence import OpfSearchSequence
from clone_all_pechas import download_pecha,git_push,setup_logger
from pathlib import Path
from os.path import exists
from uuid import uuid4
import shutil
import logging

formatter = logging.Formatter('%(message)s')


def update_works(instances,work):
    if exists("./works.yml"):
        works = OpfSearchSequence.from_yaml(Path("./works.yml"))
        works["instances"].update(instances)
    else:
        works = {
            "id":uuid4().hex,
            "title":work,
            "instances":instances
        }    

    works_yml = OpfSearchSequence.toyaml(works)
    return works_yml

def get_instances(search_path,target_opf_path,work):
    obj = OpfSearchSequence(search_path,target_opf_path,work)
    instances = obj.search_sequence()
    return instances

def get_pecha_ids():
    pecha_ids = (Path(f"./tengyurs.txt").read_text(encoding='utf-8')).splitlines()
    for pecha_id in pecha_ids:
        yield pecha_id
    """ if not exists("./processed_pechas.log"):
        for pecha_id in pecha_ids:
            yield pecha_id
    else:        
        processed_pecha_ids = (Path(f"./processed_pechas.log").read_text(encoding='utf-8')).splitlines()
        for index,pecha_id in enumerate(pecha_ids):
            last_processed_id = processed_pecha_ids[-1]
            if last_processed_id in pecha_ids[:index]:
                yield pecha_id """
       

def push_changes(target_opf_path):
    PATH_OF_GIT_REPO = rf'{target_opf_path}/.git'
    FILES = ["./index.yml"]
    MESSAGE = "updated index"
    git_push(PATH_OF_GIT_REPO,MESSAGE,FILES)
    
def delete_processed_files(target_opf_path):
    try:
        shutil.rmtree(target_opf_path)
    except OSError as e:
        print("Error: %s : %s" % (target_opf_path, e.strerror)) 

def get_instances_from_remote_opfs():
    logger = setup_logger("processed_pechas","processed_pechas.log")
    work = "chojuk"
    search_path = "./O96FB467A/O96FB467A/O96FB467A.opf/base/03EC.txt"
    pecha_ids = get_pecha_ids()
    for pecha_id in pecha_ids:
        print(pecha_id)
        #download_pecha(pecha_id,"./opfs")
        target_opf_path = f"./opfs/{pecha_id}"
        instances = get_instances(search_path,target_opf_path,work)
        if instances:
            works_yml = update_works(instances,work)
            Path("./works.yml").write_text(works_yml)
            print(f"Instnace Match at {pecha_id}")
            #push_changes(target_opf_path)
        #delete_processed_files(target_opf_path)
        logger.info(pecha_id)

if __name__ == "__main__":
    get_instances_from_remote_opfs()
    """ search_path = "./O96FB467A/O96FB467A/O96FB467A.opf/base/03EC.txt"
    target_opf_path = "opfs/IA3E40644"
    work = "chojuk"
    instances = get_instances(search_path,target_opf_path,work)
    print(instances) """
