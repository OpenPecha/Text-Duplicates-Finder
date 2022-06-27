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
        self.segment_length = 50
        first_seg = text[0:self.segment_length]
        last_seg = text[-self.segment_length:]
        self.len_of_text = len(text)
        mid = int(self.len_of_text/2)
        mid_seg = text[int(mid-self.segment_length/2):int(mid+self.segment_length/2)]
        self.diffs = (int(self.len_of_text-self.segment_length),int(mid-self.segment_length/2))
        return (first_seg,mid_seg,last_seg)

    def get_target_files(self):
        bases = list(Path(self.target_path+"/base").iterdir())
        for base in bases:
            yield base

    def fuzzy_search(self,target_file,segments): 
        first,mid,last = segments
        first_matches = self.check_matches(first,target_file)
        mid_matches = self.check_matches(mid,target_file)
        last_matches = self.check_matches(last,target_file)

        if first_matches and mid_matches and last_matches:
            print(first_matches)
            print("**************")
            print(last_matches)
            print("***********")
            matches = self.filter_matches(first_matches,mid_matches,last_matches)
            print(matches)
            
            return matches


    def check_matches(self,search_pattern,target_file):
        with open(target_file.as_posix(), 'r',encoding='utf8') as f:
            match = find_near_matches_in_file(search_pattern,f,max_l_dist=15)

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

    def normalize_matches(self,first_matches,mid_matches,last_matches):
        matches = (first_matches,mid_matches,last_matches)
        norm_matches = []
        for match in matches:
            norm_match = self.check_minimum(match)
            norm_matches.append(norm_match)
        return norm_matches

    def check_minimum(self,matches):
        min = matches[0].dist
        min_match = []
        for match in matches:
            if match.dist <= min:
                min = match.dist
        for match in matches:
            if match.dist == min:
                min_match.append(match)
        return min_match 

            

    def filter_matches(self,first_matches,mid_matches,last_matches):
        x= 0
        normalized_matches = self.normalize_matches(first_matches,mid_matches,last_matches)
        first_matches,mid_matches,last_matches = normalized_matches

        if len(first_matches) == len(mid_matches) == len(last_matches) == 1:
            matches = [(first_matches[0],last_matches[0])]
        else:
            matches = self.get_shortest_match(first_matches,mid_matches,last_matches)    
        return matches

    def get_shortest_match(self,first_matches,mid_matches,last_matches):
        lengths =[len(first_matches),len(mid_matches),len(last_matches)]
        no_of_minimums = lengths.count(min(lengths))
        actions = {1:self.one_minimum,2:self.two_minimum,3:self.three_minimum}
        action = actions.get(no_of_minimums)
        matches = action(no_of_minimums,first_matches,mid_matches,last_matches)
        return matches        

    def get_closest_match(self,match_target,match_collection,diffs):
        ref_start = match_target.start
        diff_matches={}
        for match in match_collection:
            diff = abs(match.start - ref_start)
            diff_matches.update({diff:match})
        closest_diff = min(list(diff_matches.keys()), key=lambda x:abs(x-diffs))     
        return diff_matches[closest_diff]   
            
    
    def one_minimum(self,minimum,first_matches,mid_matches,last_matches):
        first_last_diff,mid_to_end_diff = self.diffs
        matches = []
        if len(first_matches) == minimum:
            for match in first_matches:
                last_match = self.get_closest_match(match,last_matches,first_last_diff)
                matches.append((match,last_match))
        elif len(mid_matches) == minimum:
            for match in mid_matches:
                first_match = self.get_closest_match(match,first_matches,mid_to_end_diff)
                last_match = self.get_closest_match(match,last_matches,mid_to_end_diff)
                matches.append((first_match,last_match))

        else:
            for match in last_matches:
                first_match = self.get_closest_match(match,first_matches,first_last_diff)
                matches.append((first_match,match))

        return matches



    def two_minimum(self,minimum,first_matches,mid_matches,last_matches):
        first_last_diff,_ = self.diffs
        matches = []
        if len(first_matches) != minimum:
            for match in last_matches:
                first_match = self.get_closest_match(match,first_matches,first_last_diff)
                matches.append((first_match,match))
        elif len(mid_matches) != minimum:
            for first,last in zip(first_matches,last_matches):
                matches.append((first,last))
        elif len(last_matches) != minimum:
            for match in first_matches:
                last_match = self.get_closest_match(match,last_matches,first_last_diff)
                matches.append((match,last_match))        

        return matches

    def three_minimum(self,minimum,first_matches,mid_matches,last_matches):
        matches = []
        for first,_,last in zip(first_matches,mid_matches,last_matches):
            matches.append((first,last))
        return matches

    def search_sequence(self):
        instances = {}
        segments = self.get_search_segments()
        print(segments)
        for target_file in self.get_target_files():
            print(target_file)
            matches = self.fuzzy_search(target_file,segments)
            if matches:
                spans = self.get_matched_spans(matches)
                instance = self.create_index(spans,target_file)
                instances.update(instance)
        
        return instances






