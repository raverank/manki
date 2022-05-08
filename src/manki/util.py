from bs4 import BeautifulSoup, PageElement, Tag


def ensure_list(input):
    return input if isinstance(input, list) else [input]


def extract_html_between_tags(start_tag: Tag, end_tag: Tag, include_start_tag=False) -> BeautifulSoup:
    curr_tag = start_tag if include_start_tag else start_tag.next_sibling
    content = ""
    while curr_tag is not end_tag and curr_tag is not None:
        content += str(curr_tag)
        curr_tag = curr_tag.next_sibling

    return BeautifulSoup(content, features="html.parser")


def split_at_tags(name: str, soup: BeautifulSoup):
    splitted = []
    tags = soup.find_all(name)
    if tags:
        tags.append(None)
        start_tag = tags[0]
        for i in range(1, len(tags)):
            end_tag = tags[i]
            splitted.append(extract_html_between_tags(start_tag, end_tag, include_start_tag=True))
            start_tag = end_tag
    
    return splitted