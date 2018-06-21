# coding = utf-8

import json
import multiprocessing
import os
import requests
import sys

from joblib import Parallel, delayed
from lxml import etree
from io import StringIO, BytesIO

baseUrl = "https://stormshield.one/pvp/stats/"

def generateJSON(data):
    return {
        "wins": data[0],
        "top10": data[1],
        "top25": data[2],
        "kills": data[3],
        "kd": data[4],
        "matches": data[5],
        "win_p": data[6]
    }

def parse_overview(element):
    wins = int(element[0].xpath('./div[1]/a/div[1]/text()')[0])
    top10 = int(element[0].xpath('./div[2]/a/div[1]/text()')[0])
    top25 = int(element[0].xpath('./div[3]/a/div[1]/text()')[0])
    kills = int(element[0].xpath('./div[4]/div/a/div[1]/text()')[0])
    kd = float(element[0].xpath('./div[5]/div/a/div[1]/text()')[0])
    matches = int(element[0].xpath('./div[7]/div/a/div[1]/text()')[0])
    win_p = float(element[0].xpath('./div[8]/div/a/div[1]/text()')[0].replace('%', ''))
    return generateJSON((wins, top10, top25, kills, kd, matches, win_p))

def parse(element):
    wins = int(element[0].xpath('./div[2]/a/div[1]/text()')[0])
    top10 = int(element[0].xpath('./div[3]/a/div[1]/text()')[0])
    top25 = int(element[0].xpath('./div[4]/a/div[1]/text()')[0])    
    kills = int(element[0].xpath('./div[5]/div/a/div[1]/text()')[0])
    kd = float(element[0].xpath('./div[6]/div/a/div[1]/text()')[0])
    matches = int(element[0].xpath('./div[8]/div/a/div[1]/text()')[0])
    win_p = float(element[0].xpath('./div[9]/div/a/div[1]/text()')[0].replace('%', ''))
    return generateJSON((wins, top10, top25, kills, kd, matches, win_p))

def process_data(nick):
    if not os.path.exists('./data/{}.json'.format(nick)):
        r = requests.get("{}{}".format(baseUrl, nick))
        if r.status_code != 200: 
            return None

        tree = etree.parse(BytesIO(r.content), etree.HTMLParser())
        stats = {}

        try:
            stats["overview"] = parse_overview(tree.xpath('// div[@class="card group group--lifetime"]/div[2]/div[2]'))
            for gamemode in ["solo", "duos", "squads"]:
                try:
                    for element in tree.xpath('// div[@class="card group group--{}"]'.format(gamemode)):
                        platforms = {"windows": "pc", "playstation": "ps4", "xbox": "xbox"}
                        obtained_platform = element.xpath('./div[1]/div/div/h2/span[1]/@class')[0].replace("fab", "").replace("fa-", "").strip()
                        platform = platforms[obtained_platform]
                        stats["{}-{}".format(gamemode, platform)] = parse(element.xpath('./div[2]/div[2]'))
                except Exception as e: 
                    continue
        except Exception as e:
            return None

            
        with open('./data/{}.json'.format(nick), 'w', encoding='utf-8') as outfile:
            json.dump({
                "name": nick,
                "stats" : stats
            }, outfile, ensure_ascii=False)  
            return None
    else:
        return None

def main():
    fileName = "nicknames.txt"
    
    if len(sys.argv) > 1:
        fileName = sys.argv[1]

    if not os.path.exists(fileName):
        print("File '{}' does not exist.".format(fileName))
        sys.exit(-1)

    num_cores = multiprocessing.cpu_count()
    with open(os.path.join("./", fileName), 'r') as f:
        Parallel(n_jobs=2 * num_cores, backend='threading')(delayed(process_data)(nick.strip()) for nick in f.readlines())

    print("Finished processing file: {}".format(fileName))
            
            
if __name__ == '__main__':
    main()