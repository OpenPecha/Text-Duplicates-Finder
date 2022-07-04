from opf_search_sequence import OpfSearchSequence
from pathlib import Path
import yaml


def check_span(yml_path):
    works_yml = Path(yml_path)
    works = OpfSearchSequence.from_yaml(works_yml)
    instances = works["instances"]

    for instance_id in instances:
        pecha_id = instances[instance_id]["pecha_id"]
        base_id = instances[instance_id]["span"]["base"]
        path = f"opfs/{pecha_id}/{pecha_id}.opf/base/{base_id}.txt"
        text = Path(path).read_text()
        start = instances[instance_id]["span"]["start"]
        end = instances[instance_id]["span"]["end"]
        yield (text[start:start+100],text[start:end])

if __name__ == "__main__":
    path = "./works.yml"
    for spans in check_span(path):
        start_text,end_text = spans
        print(start_text)
        print("***********")
        print(end_text)
        break
