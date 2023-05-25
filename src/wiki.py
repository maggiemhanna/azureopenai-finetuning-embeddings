import pandas as pd
import wikipedia

import re
from typing import Set

import numpy as np

discard_categories = ['See also', 'References', 'External links', 'Further reading', "Footnotes",
    "Bibliography", "Sources", "Citations", "Literature", "Footnotes", "Notes and references",
    "Photo gallery", "Works cited", "Photos", "Gallery", "Notes", "References and sources",
    "References and notes",]


def filter_keywords(titles, keywords):
    """
    Get only the titles that contain the list of keywords, given a list of titles
    """
    titles = [title for title in titles if all(word in title.lower() for word in keywords)]
    
    return titles
   
def get_wiki_page(title):
    """
    Get the wikipedia page given a title
    """
    try:
        return wikipedia.page(title, auto_suggest=False)
    except wikipedia.exceptions.DisambiguationError as e:
        return wikipedia.page(e.options[0])
    except wikipedia.exceptions.PageError as e:
        return None

def recursively_find_all_pages(titles, keywords, titles_so_far=set()):
    """
    Recursively find all the pages that are linked to the Wikipedia titles in the list
    """
    all_pages = []
    
    titles = list(set(titles) - titles_so_far)
    titles = filter_keywords(titles, keywords)
    titles_so_far.update(titles)
    for title in titles:
        page = get_wiki_page(title)
        if page is None:
            continue
        all_pages.append(page)

        new_pages = recursively_find_all_pages(page.links, keywords, titles_so_far)
        for pg in new_pages:
            if pg.title not in [p.title for p in all_pages]:
                all_pages.append(pg)
        titles_so_far.update(page.links)
    return all_pages


def extract_sections(
    wiki_text: str,
    title: str,
    discard_categories: Set[str] = discard_categories,
) -> str:
    """
    Extract the sections of a Wikipedia page, discarding the references and other low information sections
    """
    if len(wiki_text) == 0:
        return []

    # find all headings and the coresponding contents
    headings = re.findall("==+ .* ==+", wiki_text)
    for heading in headings:
        wiki_text = wiki_text.replace(heading, "==+ !! ==+")
    contents = wiki_text.split("==+ !! ==+")
    contents = [c.strip() for c in contents]
    assert len(headings) == len(contents) - 1

    cont = contents.pop(0).strip()
    outputs = [(title, "Summary", cont)]
    
    # discard the discard categories, accounting for a tree structure
    max_level = 100
    keep_group_level = max_level
    remove_group_level = max_level
    nheadings, ncontents = [], []
    for heading, content in zip(headings, contents):
        plain_heading = " ".join(heading.split(" ")[1:-1])
        num_equals = len(heading.split(" ")[0])
        if num_equals <= keep_group_level:
            keep_group_level = max_level

        if num_equals > remove_group_level:
            if (
                num_equals <= keep_group_level
            ):
                continue
        keep_group_level = max_level
        if plain_heading in discard_categories:
            remove_group_level = num_equals
            keep_group_level = max_level
            continue
        nheadings.append(heading.replace("=", "").strip())
        ncontents.append(content)
        remove_group_level = max_level

    # Create a tuple of (title, section_name, content, number of tokens)
    outputs += [(title, h, c)  
                for h, c in zip(nheadings, ncontents)]
    
    return outputs


def get_wiki_pages(titles, keywords):

    # Extract Wiki Pages & subpages that correspond to the list of titles
    # Include only titles that have the given list of keywords.
    pages = recursively_find_all_pages(titles, keywords)
    print("Number of wiki pages:", len(pages))

    # Extract the different sections from pages
    res = []
    for page in pages:
        res += extract_sections(page.content, page.title)
    df = pd.DataFrame(res, columns=["title", "heading", "text"])
    df = df.drop_duplicates(['title','heading'])
    df = df.reset_index().drop('index',axis=1) # reset index
    df['words'] = df['text'].apply(lambda x: len(x.split()))
    df.insert(0, "source", "wiki")
    print("Number of wiki sections:", len(df))

    return(df)