#!/usr/bin/env python3

import requests
import traceback
import argparse
from styles import *
from bs4 import BeautifulSoup
from ebooklib import epub

def getHtml(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    try:
        htmlContent = requests.get(url, headers=headers).text
        soup = BeautifulSoup(htmlContent, "html.parser")
    except Exception as e:
        print('[!] Error while getting html!')
        print(e)
        traceback.print_exc()
        return None
    return soup

def checkUrlForKnownSources(url):
    for key in knownUrls.keys():
        if key in url:
            return knownUrls[key]
    return None

def createBasicEpub(content, title="", author="epubcomrade"):
    book = epub.EpubBook()

    # add metadata
    if (title == ""):
        title = "title"

    titleLower = title.lower().replace(" ", "_")
    book.set_identifier(titleLower)
    book.set_title(title)
    book.set_language('en')

    book.add_author(author)

    # chapter
    c1 = epub.EpubHtml(title='test1', file_name='intro.xhtml', lang='en')
    c1.content = u'<html><head></head><body>'
    c1.content += u'<h1>' + title + u'</h1>'
    c1.content += content
    c1.content += u'</body></html>'

    # add chapters to the book
    book.add_item(c1)
    
    # create table of contents
    # - add section
    # - add auto created links to chapters
    # book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
                 # (epub.Section('Languages'),
                 # (c1, c2, c3))
                # )
    # book.toc = ((c1, c2))

    # add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # create spine
    # book.spine = ['nav', c1]
    book.spine = [c1]

    # create epub file
    filename = titleLower + '.epub'
    epub.write_epub(filename, book, {})
    print("[*] Written to", filename)

def miaParseAndPublish(url):
    pass

def idomParseAndPublish(url):
    soup = getHtml(url)
    section = soup.find("section")
    paragraphs = soup.find_all("p")
    title = soup.find(class_="article-title").text

    # Sometimes there are preceeding and trailing space characters in the title. remove em
    while(title[0] == " "):
        title = title[1:]

    while(title[-1] == " " and len(title) > 0):
        title = title[:-1]

    if (len(title) == 0):
        title = "Title"
    print("[*] Title:", title)
    content = ""
    for p in paragraphs:
        content += "<p>" + p.text + "</p>"
    createBasicEpub(content, title=title, author="IDOM")

def help():
    pass

### MAIN FUNCTIONALITY ###

knownUrls = {"marxist.com" : {"host":"IDOM", "fn":idomParseAndPublish},
             "marxists.org" :{"host":"MIA", "fn":miaParseAndPublish}
            }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to make a book out of")
    args = parser.parse_args()
    host = checkUrlForKnownSources(args.url)
    if (host == None):
        print("[!] Couldnt find host")
        return
    print("[*] URL:", args.url)
    print('[*] Host:', host['host'])
    hostFn = host['fn']
    hostFn(args.url)
    
if __name__ == '__main__':
    main()
