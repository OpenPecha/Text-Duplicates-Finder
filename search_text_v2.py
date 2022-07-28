from pathlib import Path
from fuzzysearch import find_near_matches_in_file
from fuzzywuzzy import fuzz
from seg_data import search_Seg

target_text = ""
def fuzzy_search(target_file,search_segment):
    d = len(search_segment)*0.2
    with open(target_file.as_posix(), 'r',encoding='utf8') as f:
        match = find_near_matches_in_file(search_segment,f,max_l_dist=int(d))
    return match

def get_search_target(target_file:Path):
    obj = search_Seg()
    text = target_file.read_text()
    text = text.replace("\n","")
    chunks, chunk_size = len(text), 50
    splitted_chunks = [ text[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    if len(splitted_chunks[-1]) < 40:
        splitted_chunks[-2] = splitted_chunks[-2]+splitted_chunks[-1]
        splitted_chunks.pop()

    for chunk in splitted_chunks:
        obj.push(chunk)
    return obj


def main(search_file:Path,target_file:Path):
    global target_text 
    target_text = target_file.read_text()
    seg_obj = get_search_target(search_file)
    first_seg_node = seg_obj.getFirst()
    middle_seg_node = seg_obj.getMiddle(first_seg_node)
    last_seg_node = seg_obj.getLast()
    first_matches = check_instances(target_file,first_seg_node.data)
    mid_matches = check_instances(target_file,middle_seg_node.data)
    last_matches = check_instances(target_file,last_seg_node.data)
    if first_matches and mid_matches and last_matches:
        print(first_matches)
        print(last_matches)
        first_match = check_matches_in_right_window(first_matches,first_seg_node)
        last_match = check_matches_in_left_window(last_matches,last_seg_node)
        print(first_match)
        print(last_match)
    else:
        print("No match")


def check_matches_in_right_window(matches,node):
    global target_text
    most_r = 0
    cor_match = ""
    for match in matches:
        r = 0
        cur_start = match.end
        cur_end = match.end+50
        for i in range(10):
            node = node.next
            target_chunk = target_text[cur_start:cur_end]
            search_chunk = node.data
            r += fuzz.ratio(search_chunk,target_chunk)
        cur_start+=50
        cur_end+=50
        if r > most_r:
            most_r = r
            cor_match = match
    return cor_match


def check_matches_in_left_window(matches,node):
    global target_text
    most_r = 0
    cor_match = ""

    for match in matches:
        r = 0
        cur_start = match.start-50
        cur_end = match.start
        for i in range(10):
            node = node.prev
            target_chunk = target_text[cur_start:cur_end]
            search_chunk = node.data
            r+=fuzz.ratio(search_chunk,target_chunk)
        cur_start-=50
        cur_end-=50
        if r > most_r:
            most_r = r
            cor_match = match    


    return cor_match

def check_instances(search_file,target):
    matches = fuzzy_search(search_file,target)
    #closest_match = get_closest_match(matches)
    return matches


def get_closest_match(matches):
    min = matches[0]
    for match in matches:
        if match.dist <= min.dist:
            min = match
    return min


if __name__ == "__main__":
    search_path = Path("O96FB467A/O96FB467A/O96FB467A.opf/base/03EC.txt")
    target_path = Path("opfs_tengyur/I5AD14136/I5AD14136.opf/base/BF5B.txt")
    target_text = target_path.read_text()
    main(search_path,target_path)