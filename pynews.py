import csv
from lxml import html
import requests
import re
import sys
from time import sleep
from urllib.parse import urljoin


ARCHIVES = [
    ('Python Weekly', 'https://us2.campaign-archive.com/home/?u=e2e180baf855ac797ef407fc7&id=9e26887fc5'),
    ("Pycoder's Weekly", 'https://us4.campaign-archive.com/home/?u=9735795484d2e4c204da82a29&id=64134e0a27'),
]


IGNORE_RE = re.compile(r'''
    twitter\.com / [^/]+ $
    |
    //translate\.google\.com/
    |
    \.list-manage\.com/
    |
    \.campaign-archive\.com/
    |
    ^javascript:
    |
    eepurl.com
    |
    mailchi.mp
    |
    \.forward-to-friend\.com/
''', re.VERBOSE)


def get_email_page_urls(archive_url, xpath_selector='//li/a'):
    """Yield URLs for individual email pages from given archive page."""
    response = requests.get(archive_url)
    tree = html.fromstring(response.content)
    for link in tree.xpath(xpath_selector):
        yield from (
            urljoin(archive_url, value)
            for (key, value) in link.items()
            if key == 'href'
        )


def get_links_from_email_page(email_page_url, xpath_selector='//a'):
    """Yield URLs for all links in given email page."""
    response = requests.get(email_page_url)
    tree = html.fromstring(response.content)
    for link in tree.xpath(xpath_selector):
        yield next(
            (link.text, urljoin(email_page_url, value))
            for (key, value) in link.items()
            if key == 'href'
        )


def main():
    """
    Write CSV of archived links to standard output.
    
    Format: ARCHIVE,TITLE,URL
    """
    writer = csv.writer(sys.stdout)
    for name, url in ARCHIVES:
        for url in get_email_page_urls(url):
            for text, url in get_links_from_email_page(url):
                if text and text.strip() and not IGNORE_RE.search(url):
                    writer.writerow((name, text, url))
            sleep(0.25)


if __name__ == "__main__":
    main()
