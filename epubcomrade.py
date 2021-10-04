#!/usr/bin/env python3

import traceback
import argparse
import sys
import re
from styles import *
from common import *
try:
    import requests
    from bs4 import BeautifulSoup
    from bs4 import UnicodeDammit
    from ebooklib import epub
except Exception as e:
    print(e)
    traceback.print_exc()
    print("[!] Youll need the libraries: \"requests\", \"bs4\", \"EbookLib\". Get em from pip3!")
    sys.exit(1)

def removeTrailingWhitespace(str):
    cropped = str
    while(cropped[0] == " " or cropped[0] == "\n"):
        cropped = cropped[1:]
    while((cropped[-1] == " " or cropped[-1] == "\n") and len(cropped) > 0):
        cropped = cropped[:-1]
    return cropped

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

    idString = re.sub('[^0-9a-zA-Z\ ]+', '', title.lower()).replace(" ", "_") # Remove all non-alphanumeric chars from filename
    book.set_identifier(idString)
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
    filename = idString + '.epub'
    epub.write_epub(filename, book, {})
    print("[*] Written to", filename)

def miaParseAndPublish(url):
    soup = getHtml(url)
    body = soup.body
    info = soup.find(class_="information")
    paragraphs = soup.find_all(re.compile('(h[1-6])|(p)')) # Find all headers (titles) and paragraphs
    content = ""
    title = soup.find("title")
    if (title == None):
        title = url
        print('[!] Title not found. Going with URL as the title')
    else:
        title = title.text
        print("[*] Title:", title)
    for p in paragraphs:
        if (p.name[0] != 'h' and p.name[0] != 'p'):
            continue # TODO HACK This is due to the regex that finds all h and p tags. it catches unwanted tags
        if ('class' in p.attrs and 'information' in p.attrs['class']):
            content += '<hr class="division">' + "<p>" + p.text + "</p>" + '<hr class="division">'
        else:
            content += "<" + p.name + ">" + p.text + "</" + p.name + ">"
    createBasicEpub(content, title=title)
    return True

def idomParseAndPublish(url):
    soup = getHtml(url)
    section = soup.find("section")
    paragraphs = section.find_all(re.compile('(h[1-6])|(p)'))
    title = soup.find(class_="article-title").text
    authorText = "IDOM"

    # Get article author
    try:
        authorPerson = soup.find(itemprop="author").text

        # Strip trailing spaces
        authorPerson = authorPerson.strip()
        authorText += " - " + authorPerson
    except AttributeError as e:
        print('[!] Couldnt find author')
    
    # Get date published
    datePublished = "-"
    try:
        datePublished = soup.find(itemprop="datePublished").text
    except AttributeError as e:
        print("[!] Couldnt find publish date")

    # Sometimes there are preceeding and trailing space characters in the title. remove em
    title = title.strip()

    if (len(title) == 0):
        title = "Title"

    print("[*] Title:", title)
    print("[*] Author:", authorPerson)
    print("[*] Date published:", datePublished)
    content = "<p>" + authorText + ", " + datePublished + "</p>" + '<hr class="division">'
    for p in paragraphs:
        if (p.name[0] != 'h' and p.name[0] != 'p'):
            continue # TODO HACK This is due to the regex that finds all h and p tags. it catches unwanted tags
        if ('class' in p.attrs and 'article-title' in p.attrs['class']):
            continue # We already print the title ourselves. TODO, maybe how about not doing that? 
        content += "<" + p.name + ">" + p.text + "</" + p.name + ">"
    createBasicEpub(content, title=title, author=authorText)
    return True

def socialistAppealParseAndPublish(url):
    soup = getHtml(url)
    title = soup.find(class_="article-title")
    authorPerson = soup.find(itemprop="author")
    abstract = soup.find(class_="metaintro")
    content = soup.find(class_="article-content")
    print(title.text.strip())
    print(authorPerson.text.strip())
    print(abstract.text.strip())
    print(content.text.strip())
    return True

def help():
    print(INTRO_STR)
    print(HELP_STR)

### MAIN FUNCTIONALITY ###

knownUrls = {"marxist.com" : {"host":"IDOM", "fn":idomParseAndPublish},
             "marxists.org" :{"host":"MIA", "fn":miaParseAndPublish},
             "socialist.net" : {"host":"SOCIALIST APPEAL", "fn":socialistAppealParseAndPublish}
            }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to make a book out of")
    print(INTRO_STR)
    args = parser.parse_args()
    host = checkUrlForKnownSources(args.url)
    if (host == None):
        print("[!] Couldnt find host")
        return
    print("[*] URL:", args.url)
    print('[*] Host:', host['host'])
    hostFn = host['fn']
    ret = hostFn(args.url)
    if (ret):
        print('[*] Done!')
    else:
        print('[!] Error(s) happened during execution!')
    
if __name__ == '__main__':
    main()
