# coding = utf-8

import os
import sys

resultsFolder = "./data"

def main():
    count = 0
    filenames = os.listdir(resultsFolder)
    with open('./dataset.json', 'w') as outfile:
        for fname in filenames:
            with open(os.path.join(resultsFolder, fname), 'r') as infile:
                for line in infile:
                    count += 1
                    outfile.write("{},\n".format(line))
                    print("{} items written".format(count))

if __name__ == '__main__':
    main()