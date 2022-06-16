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
        self.diffs = (len_of_text-50,mid-25)
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
            matches = self.filter_matches(first_match,mid_match,last_match)
            return matches


    def check_matches(self,search_pattern,target_file):
        with open(target_file.as_posix(), 'r',encoding='utf8') as f:
            match = find_near_matches_in_file(search_pattern,f,max_l_dist=10)
        return match


    def create_index(self,spans,target_file):
        annotations = self.get_annotations(spans,target_file)
        Path(f"{self.target_path}/index.yml").write_text(annotations)
        instances = self.get_instances(spans,target_file)
        return instances

    def get_annotations(self,spans,target_file):
        page_annotaions = {}

        for span in spans:
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
            page_annotaions.update(page_annotaion)
        if exists(f"{self.target_path}/index.yml"):
            index = self.from_yaml(Path(f"{self.target_path}/index.yml"))
            index["annotations"].update(page_annotaions)
        else:
            index = {
            "id":uuid4().hex,
            "annotatation_type":"index",
            "annotations":page_annotaions
            }

        index_yml = self.toyaml(index)
        
        return index_yml


    def get_matched_spans(self,matches):
        match_list = []
        for match in matches:
            first_match,last_match = match
            match_list.append((first_match.start,last_match.end))
        return match_list

    
    @staticmethod
    def toyaml(dict):
        return yaml.safe_dump(dict, sort_keys=False, allow_unicode=True)

    @staticmethod
    def from_yaml(yml_path):
        return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

    @staticmethod
    def get_work_id():
        return "W" + "".join(random.choices(uuid4().hex, k=8)).upper()

    def get_instances(self,spans,target_file):
        instances = {}
        for span in spans:
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
            instances.update(instance)
        return instances

    def filter_matches(self,first_match,mid_match,last_match):
        matches = []
        if len(first_match) == len(mid_match) == len(last_match) == 1:
            matches.append((first_match,last_match))
        else:
            matches = self.get_shortest_match(first_match,mid_match,last_match)    
        return matches

    def get_shortest_match(self,first_match,mid_match,last_match):
        lengths =[len(first_match),len(mid_match),len(last_match)]
        minimum = min(lengths)
        actions = {1:self.get_one_minimum,2:self.get_two_minimum,3:self.get_three_minimum}
        action = actions.get(minimum)
        matches = action(minimum,first_match,mid_match,last_match)
        return matches        

    def get_closest_match(self,match_target,match_collection,diffs):
        ref_start = match_target[0].start
        diff_matches={}
        for match in match_collection:
            diff = match.start - ref_start
            diff_matches.update({diff:match})
        closest_diff = min(list(diff_matches.keys()), key=lambda x:abs(x-diffs))     
        return diff_matches[closest_diff]   
            
    
    def get_one_minimum(self,minimum,first_match,mid_match,last_match):
        first_last_diff,mid_to_end_diff = self.diffs
        if len(first_match) == minimum:
            last_match = self.get_closest_match(first_match,last_match,first_last_diff)
        elif len(mid_match) == minimum:
            first_match = self.get_closest_match(mid_match,first_match,mid_to_end_diff)
            last_match = self.get_closest_match(mid_match,last_match,mid_to_end_diff)
        else:
            first_match = self.get_closest_match(last_match,first_match,first_last_diff)

        return [(first_match,last_match)]



    def get_two_minimum(self,minimum,first_match,mid_match,last_match):
        first_last_diff,_ = self.diffs
        matches = []
        if len(first_match) != minimum:
            for match in last_match:
                first_match = self.get_closest_match(match,first_match,first_last_diff)
                matches.append((first_match,match))
        elif len(mid_match) != minimum:
            for first,last in zip(first_match,last_match):
                matches.append((first,last))
        elif len(last_match) != minimum:
            for match in first_match:
                last_match = self.get_closest_match(match,last_match,first_last_diff)
                matches.append((match,last_match))        

        return matches

    def get_three_minimum(self,minimum,first_match,mid_match,last_match):
        matches = []
        for first,_,last in zip(first_match,mid_match,last_match):
            matches.append((first,last))
        return matches

    def search_sequence(self):
        instances = {}
        segments = self.get_search_segments()
        print(segments)
        for target_file in self.get_target_files():
            matches = self.fuzzy_search(target_file,segments)
            if matches:
                print(f"MATCH at {target_file}")
                print(matches)
                spans = self.get_matched_spans(matches)
                instance = self.create_index(spans,target_file)
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

