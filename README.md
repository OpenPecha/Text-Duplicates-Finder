# text-search
Various approaches to find a text in a corpus

- dowload all opfs in the OpenPecha archive
- generate a corpus with views of all normalized views
- fuzzy search several small substrings from start, middle and end of text
    - if match is found check the length between start and end (versions might get up to 150% or original because of notes or page headers, commentaries can get 200% or more)
    - add table of content layer with the coordinate of the text
    - add the text instance ID to the work .yml


## Interesting Links
### Fuzzy search
- https://pypi.org/project/fuzzysearch/
- https://github.com/seatgeek/thefuzz

### Full text search
- https://towardsdatascience.com/natural-language-processing-document-search-using-spacy-and-python-820acdf604af
- https://freecontent.manning.com/the-cool-way-to-search-text/
- https://github.com/rtmigo/skifts_py
- https://github.com/proycon/pynlpl
- https://github.com/jorzel/postgres-full-text-search
- https://github.com/mchaput/whoosh
