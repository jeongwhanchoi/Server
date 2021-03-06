# usr/bin/python27


import os, sys, requests
from bs4 import BeautifulSoup


class Extractor ():
    global parse_article
    global tag2md

    def __init__(self):
        return None

    def extract(self, URL):
        res = requests.get(URL)
        if (res.status_code == 200 and 'content-type' in res.headers and res.headers.get('content-type').startswith('text/html')):
            article = parse_article(res.text)
            # return article['title'] # return only the headline
            return article
        else:
            print("extraction is failed")

    def parse_article(text):
        soup = BeautifulSoup(text, 'html.parser')
        # print(soup.prettify()) # print html structure in prettier ways

        # find the article title.
        h1 = soup.find('h1', {'class': 'pg-headline'})

        # find the common parent for <h1> and all <p>s.
        root = h1
        while root.name != 'body' and len(root.find_all('p')) < 5:
            root = root.parent

        if len(root.find_all('p')) < 5:
            return None

        # find all the content elements.
        ps = root.find_all(['p', 'div'], {'class': ['zn-body__paragraph speakable', 'zn-body__paragraph']})
        article_contents = [tag2md(p).encode('ascii') for p in ps]

        content = "".join(article_contents)

        return {'title': h1.text.encode('ascii'), 'content': content}

    def tag2md(tag):
        if tag.name == 'p':
            return tag.text
        elif tag.name == 'div':
            return tag.text
        # elif tag.name == 'h1':
        #     text = tag.text + '\n' + "=" *len(tag.text)
        #     return text
        # elif tag.name == 'h2':
        #     text = tag.text + '\n' + "-" *len(tag.text)
        #     return text
        # elif tag.name in ['h3', 'h4', 'h5', 'h6']:
        #     text = "#" * int(tag.name[1:]) + '\n' + tag.text
        #     return text
        # elif tag.name == 'pre':
        #     text = '\n' + tag.text + '\n'
        #     return text

extractor = Extractor()

if __name__ == "__main__":
    print("extracted newsInfo: \n{0}".format(extractor.extract(sys.argv[1])))
