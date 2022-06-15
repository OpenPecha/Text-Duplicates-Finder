from pathlib import Path
from fuzzysearch import find_near_matches_in_file
from os.path import exists
import random
from uuid import uuid4
import yaml

class OpfSearchSequence:

    def __init__(self,search_sequence_path,target_opf_path,work):
        self.search_sequence_path = search_sequence_path
        self.target_path = target_opf_path+"/"+Path(target_opf_path).stem+".opf"
        self.work =work

    def get_search_segments(self):
        text = Path(self.search_sequence_path).read_text(encoding="utf-8")
        first_seg = text[0:50]
        last_seg = text[-50:]
        len_of_text = len(text)
        mid = int(len_of_text/2)
        mid_seg = text[mid-25:mid+25]
        return (first_seg,mid_seg,last_seg)

    def get_target_files(self):
        bases = list(Path(self.target_path+"/base").iterdir())
        for base in bases:
            yield base

    def fuzzy_search(self,target_file,segments): 
        first,mid,last = segments
        first_match = self.check_matches(first,target_file)
        mid_match = self.check_matches(mid,target_file)
        last_match = self.check_matches(last,target_file)

        if first_match and mid_match and last_match:
            return (first_match,last_match)


    def check_matches(self,search_pattern,target_file):
        with open(target_file.as_posix(), 'r',encoding='utf8') as f:
            match = find_near_matches_in_file(search_pattern,f,max_l_dist=10)
        return match


    def create_index(self,span,target_file):
        annotations = self.get_annotations(span,target_file)
        Path(f"{self.target_path}/index.yml").write_text(annotations)
        instance = self.get_instance(span,target_file)
        return instance

    def get_annotations(self,span,target_file):

        start,end = span
        span = {
            "start":start,
            "end":end
        }
        page_annotaion = {uuid4().hex:{
            "work":self.work,
            "work_id":self.get_work_id(),
            "base":target_file.stem,
            "span":span
        }
        }
        if exists(f"{self.target_path}/index.yml"):
            index = self.from_yaml(Path(f"{self.target_path}/index.yml"))
            index["annotations"].update(page_annotaion)
        else:
            index = {
            "id":uuid4().hex,
            "annotatation_type":"index",
            "annotations":page_annotaion
            }

        index_yml = self.toyaml(index)
        
        return index_yml


    def get_matched_span(self,match):
        first_match,last_match = match
        return (first_match.start,last_match.end)

    
    @staticmethod
    def toyaml(dict):
        return yaml.safe_dump(dict, sort_keys=False, allow_unicode=True)

    @staticmethod
    def from_yaml(yml_path):
        return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

    @staticmethod
    def get_work_id():
        return "W" + "".join(random.choices(uuid4().hex, k=8)).upper()

    def get_instance(self,span,target_file):
        start,end = span
        instance = {
            uuid4().hex:{
                "pecha_id":Path(self.target_path).stem,
                "span":{
                    "base":target_file.stem,
                    "start":start,
                    "end":end
                }
            }
        }
        return instance

    def filter_matches(self,matches):
        matches_list = []
        for match in matches:
            matches_list.append(match[-1])
        return tuple(matches_list) 


    def search_sequence(self):
        instances = {}
        segments = self.get_search_segments()
        for target_file in self.get_target_files():
            match = self.fuzzy_search(target_file,segments)
            if match:
                print(f"MATCH at {target_file}")
                match = self.filter_matches(match)
                span = self.get_matched_span(match)
                instance = self.create_index(span,target_file)
                instances.update(instance)
        
        return instances

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



if __name__ == "__main__":
    search_path = "./opfs/O96FB467A/O96FB467A/O96FB467A.opf/base/03EC.txt"
    target_opf_path = "./opfs/P000791"
    work = "chojuk"
    instances = get_instances(search_path,target_opf_path,work)
    works_yml = update_works(instances,work)
    Path("./works.yml").write_text(works_yml)

#module to handle if there is more than one match in first,mid,last
