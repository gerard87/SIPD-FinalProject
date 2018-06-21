# coding = utf-8

import multiprocessing
import requests
import sys

from joblib import Parallel, delayed
from lxml import etree
from io import StringIO, BytesIO

num_pages = 2

start = 1
end = 3

allowed_platforms = ["pc", "ps4", "xb1"]
baseUrl = "https://www.stormshield.one/pvp/"
platform = None

flatten = lambda l: [item for sublist in l for item in sublist]

def get_usernames(page):
    url = "{}solo/{}?page={}".format(baseUrl, platform, page) if platform else "{}?page={}".format(baseUrl, page)
    r = requests.get(url)
    tree = etree.parse(BytesIO(r.content), etree.HTMLParser())
    usernames = []

    for row in tree.xpath('// table[@class="table table-striped"]/tbody/tr'):
        item = row.xpath('./td[3]/a/text()')
        if len(item) > 0: usernames.append(item[0])

    return usernames

def main(): 
    num_cores = multiprocessing.cpu_count()
    results = Parallel(n_jobs=2 * num_cores)(delayed(get_usernames)(i) for i in range(start, end + 1))
    fileName = 'nicknames_{}_pages_{}-{}.txt'.format(platform if platform else "all", start, end)
    print("Writing data to file: '{}'".format(fileName))
    with open(fileName, 'w') as f:
        for item in flatten(results): f.write("{}\n".format(item))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv == '-h':
            print("Usage: {} start end [pc, xb1, ps4]".format(sys.argv[0]))
        else:
            start = int(sys.argv[1])
            end = int(sys.argv[2])
    if len(sys.argv) > 3:
        platform = sys.argv[3]
        if platform not in allowed_platforms:
            print("Platform '{}' not allowed. Please use one of the following: ".format(platform), allowed_platforms)
            sys.exit(-1)

    main()