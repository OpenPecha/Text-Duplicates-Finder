from pathlib import Path
from fuzzysearch import find_near_matches_in_file


def check_increased_window(matches,original_text,search_text):
    for match in matches:
        for cur_match in match:
            explore_window(cur_match,original_text,search_text)


def explore_window(match,original_text,search_text):
    matches = []
    start,end = match.start,match.end
    for n in range(10):
        search_seg = search_text[end:end+50]
        match = fuzzy_search(original_text,search_seg)
        end = end+50
        if match:
            matches.append("true")
    return matches


def check_instances(search_file:Path,search_target:list):
    first_segment = search_target[0]
    last_segment = search_target[-1]
    mid_segment = search_target[int(len(search_target)/2)]
    first_match = fuzzy_search(search_file,first_segment)
    last_match = fuzzy_search(search_file,last_segment)
    mid_match = fuzzy_search(search_file,mid_segment)
    if first_match and mid_match and last_match:
        matches = (first_match,mid_match,last_match)
        has_instance = check_increased_window(matches)

def fuzzy_search(target_file,search_segment):
    with open(target_file.as_posix(), 'r',encoding='utf8') as f:
        match = find_near_matches_in_file(search_segment,f,max_l_dist=15)
    return match

def get_search_target(target_file:Path):
    text = target_file.read_text()
    text = text.replace("\n","")
    chunks, chunk_size = len(text), 50
    splitted_chunks = [ text[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    return splitted_chunks


def main(search_file:Path,target_file:Path):
    search_target = get_search_target(target_file)
    check_instances(search_file,search_target)

    