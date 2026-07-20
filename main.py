#!/usr/bin/python

import feedparser
import argparse
from datetime import datetime, date
from pg import pg_connect, create_table

parser = argparse.ArgumentParser() #create parser
parser.add_argument("-w", "--writehtml", action="store_true", help="write html with downloaded feeds")
parser.add_argument("-d", "--database", action="store_true", help="write feeds to database")
parser.add_argument("-t", "--createtable", action="store_true", help="creates table if dont't already exist")
argument = parser.parse_args()

rss_url = ['https://feedexample.com/feed.xml'] #list with feeds
filename = "intel_report.html"

def write_rss_html():
    result_header =f"<html lang=\"pt-BR\"><head><meta charset=\"UTF-8\"><title>Intel Report - %s</title></head>\n" %(date.today())
    result_string = ""
    result_end = "\n</html>"
    for i in rss_url:
        rss_feed = feedparser.parse(i)
        if rss_feed.status == 200:
            try:
                result_string+=(f"<h2>Feed Title: %s</h2>" %(rss_feed.feed.title))
                result_string+=(f"<strong>Collected @ %s</strong>" %(datetime.now()))
            except:
                pass
            for entry in rss_feed.entries:
                result_string+=("<p><strong>[+] %s - <a href=\"%s\" rel=\"noopener noreferrer nofollow\" target=\"_blank\">Reference link</a> - %s</strong><br>%s</p>" %(entry.title, entry.link, entry.published, entry.description))
        else:
            print("Failed to get RSS feed. Status code:", rss_feed.status)
    write_file(result_header+result_string+result_end)

def get_rss():
    for i in rss_url:
        rss_feed = feedparser.parse(i)
        if rss_feed.status == 200:
            try:
                for entry in rss_feed.entries:
                    result = {
                        "source": rss_feed.feed.title,
                        "title": entry.title,
                        "url": entry.link,
                        "published": entry.published,
                        "content": entry.description,
                        "collected_at": datetime.now()
                    }
                    pg_connect(result)
            except:
                pass
        else:
            print("Failed to get RSS feed. Status code:", rss_feed.status)


def write_file(i):
    with open(str(filename), 'w+') as f:
        f.write('%s\n' %i)
        print("File written successfully")
        f.close()

if __name__ == '__main__':
    if (argument.writehtml):
        write_rss_html()
    if (argument.database):
        get_rss()
    if (argument.createtable):
        create_table()
