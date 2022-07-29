from pathlib import Path
import search
import pandas as pd


def main():
    dirs = []
    search_text = Path(r"C:\Users\ASUS\Desktop\z\Text-Duplicates-Finder\O96FB467A\O96FB467A\O96FB467A.opf\base\sample_base.txt").read_text(encoding='utf-8')
    text = search_text.replace("\n","")
    chunks, chunk_size = len(text), 50
    splitted_chunks = [ text[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    for chunk in splitted_chunks:
        dir = search.main(chunk)
        dirs.extend(dir)

    most_matched = filter_most_matched(dirs,splitted_chunks)
    print(most_matched)

def filter_most_matched(dirs,splitted_chunks):
    most_matched = []
    counts = pd.Series(dirs).value_counts(ascending=False)
    for dir,count in counts.items():
        if count/len(splitted_chunks) > 0.7:
            most_matched.append(dir)
    return most_matched


if __name__ == "__main__":
    main()