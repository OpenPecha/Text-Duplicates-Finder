from pathlib import Path
from fuzzysearch import find_near_matches_in_file
from seg_data import search_Seg



def fuzzy_search(target_file,search_segment):
    print(search_segment)
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
    seg_obj = get_search_target(target_file)
    first_head = seg_obj.getFirst()
    middle = seg_obj.getMiddle(first_head)
    last = seg_obj.getLast()
    print(first_head.data)
    print(first_head.next.data)
    print(middle.data)
    print(middle.next.data)
    print(last.data)
    #check_instances(search_file,seg_obj)


def check_instances(search_file,seg_obj:search_Seg):
    first_match = fuzzy_search(search_file,seg_obj.getFirst())
    #mid_match = fuzzy_search(search_file,seg_obj.getMiddle())
    last_match = fuzzy_search(search_file,seg_obj.getLast())
    print(first_match)
    print(last_match)
    
if __name__ == "__main__":
    search_path = Path("O96FB467A/O96FB467A/O96FB467A.opf/base/03EC.txt")
    target_path = Path("opfs_tengyur/I5A3E81FD/I5A3E81FD.opf/base/FE32B.txt")
    main(target_path,search_path)