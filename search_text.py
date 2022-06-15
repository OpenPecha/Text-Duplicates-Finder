from pathlib import Path
from fuzzysearch import find_near_matches_in_file
import threading
import random
from uuid import uuid4
import yaml

class OpfSearchSequence:

    def __init__(self,search_sequence_path,target_opf_path):
        self.search_sequence_path = search_sequence_path
        self.target_path = target_opf_path+"/"+Path(target_opf_path).stem+".opf"

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

        """ first_thread = threading.Thread(target=check_matches,args=(first,text))
        mid_thread = threading.Thread(target=check_matches,args=(mid,text))
        last_thread = threading.Thread(target=check_matches,args=(last,text))
        
        first_thread.start()
        mid_thread.start()
        last_thread.start()

        first_thread.join()
        mid_thread.join()
        last_thread.join() """

        if first_match and mid_match and last_match:
            return (first_match,last_match)


    def check_matches(self,search_pattern,target_file):
        with open(target_file.as_posix(), 'r',encoding='utf8') as f:
            match = find_near_matches_in_file(search_pattern,f,max_l_dist=10)
        return match


    def create_index(self,span,target_file):
        annotations,spans = self.get_annotations(span,target_file)
        annotations_yml = self.toyaml(annotations)
        Path(f"{self.target_path}/index.yml").write_text(annotations_yml)
        instance = self.add_instances(spans)
        return instance

        """ opf = OpenPechaFS(path=target_path)
        annotations,spans=self.get_annotations(span,base_file)
        index = Layer(annotation_type=LayerEnum.index,annotations=annotations)
        opf._index = index
        opf.save_index()
        instance = self.add_instances(spans,target_path)
        return instance """

    def get_annotations(self,span,target_file):
        page_annotations = {}
        spans = {}
        start,end = span
        spans.update({uuid4().hex:{
            "base":target_file.stem,
            "start":start,
            "end":end
        }})
        page_annotaion = {uuid4().hex:{
            "work":"chojuk",
            "work_id":self.get_work_id(),
            "spans":spans
        }
        }
        page_annotations.update(page_annotaion)
        return page_annotations,spans


    def get_matched_span(self,match):
        first_match,last_match = match
        return (first_match.start,last_match.end)

    def create_work(self,instances):
        work = {
            "id":uuid4().hex,
            "title":"chojuk",
            "instances":instances
        }

        return work
    
    @staticmethod
    def toyaml(dict):
        return yaml.safe_dump(dict, sort_keys=False, allow_unicode=True)

    @staticmethod
    def from_yaml(yml_path):
        return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

    @staticmethod
    def get_work_id():
        return "W" + "".join(random.choices(uuid4().hex, k=8)).upper()

    def add_instances(self,spans):
        instance = {
            uuid4().hex:{
                "pecha_id":Path(self.target_path).stem,
                "spans":spans
            }
        }
        return instance

    def filter_matches(self,matches):
        matches_list = []
        for match in matches:
            matches_list.append(match[-1])
        return tuple(matches_list) 


    def search_sequence(self):
        instances = []
        segments = self.get_search_segments()
        for target_file in self.get_target_files():
            match = self.fuzzy_search(target_file,segments)
            if match:
                print(f"match at {target_file}")
                match = self.filter_matches(match)
                span = self.get_matched_span(match)
                instance = self.create_index(span,target_file)
                instances.append(instance)
        work = self.create_work(instance)
        return work


if __name__ == "__main__":
    search_path = "./opfs/O96FB467A/O96FB467A/O96FB467A.opf/base/03EC.txt"
    target_opf_path = "./opfs/P000791"
    obj = OpfSearchSequence(search_path,target_opf_path)
    work = obj.search_sequence()
    print(work)

#module to handle if there is more than one match in first,mid,last
