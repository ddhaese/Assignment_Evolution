#!/usr/bin/python

from sys import argv, exit
from getopt import getopt, GetoptError
from re import search
import pandas as pd
from uuid import uuid4


class GithistInterpreter:
    def __init__(self, argv):
        self.inputFileName = ""
        self.summary = []
        self.curFiles = {}

        usage = "Usage: githist.py -i <git_log_input> -o <output_file>"

        try:
            opts, args = getopt(argv, "hi:o:")
        except GetoptError:
            print(usage)
            exit(2)

        for opt, arg in opts:
            if opt == '-h':
                print(usage)
                exit()
            elif opt == "-i":
                self.inputFileName = arg
            elif opt == "-o":
                self.outputFileName = arg

    def parse(self):
        with open(self.inputFileName) as inputFile:
            for rawResultLine in inputFile.readlines():
                r = search("^Processing repo (.*) \.\.\.", rawResultLine)

                if r:
                    self.curRepo = r.group(1)
                    self.curFiles = {}
                    self.curCommit = ""
                    self.curAuthor = ""
                    self.curDate = ""
                    print("REPO: ", self.curRepo,)
                    continue

                r = search("^commit (.*)", rawResultLine)

                if r:
                    self.curCommit = r.group(1)
                    print("COMMIT: ", self.curCommit,)
                    continue

                r = search("^Author: (.*) \<.*\>", rawResultLine)

                if r:
                    self.curAuthor = r.group(1)
                    print("AUTHOR: ", self.curAuthor,)
                    continue

                r = search("^Date:   (.*)", rawResultLine)

                if r:
                    self.curDate = r.group(1)
                    print("DATE: ", self.curDate,)
                    continue

                # Markdown File rename
                r = search("([0-9]+)\t([0-9]+)\t(.*) => (.*)", rawResultLine)

                if r:
                    lineAddCount = r.group(1)
                    lineDelCount = r.group(2)
                    oldFile = r.group(3).strip().replace("\"", "")
                    newFile = r.group(4).strip().replace("\"", "")

                    print(f"RENAME: \"{oldFile}\" => \"{newFile}\"")

                    if oldFile in self.curFiles:
                        self.curFiles[newFile] = self.curFiles[oldFile]
                    else:
                        self.curFiles[newFile] = uuid4().hex

                    if lineAddCount != "0" or lineDelCount != "0":
                        self.summary.append([
                            self.curRepo, self.curCommit,
                            self.curAuthor, self.curDate, self.curFiles[newFile],
                            newFile, lineAddCount, lineDelCount, "lines"])

                    continue

                # Bin File rename
                r = search("-\t-\t(.*) => (.*)", rawResultLine)

                if r:
                    oldFile = r.group(1).strip().replace("{", "").replace("\"", "")
                    newFile = r.group(2).strip().replace("}", "").replace("\"", "")

                    print(f"RENAME: \"{oldFile}\" => \"{newFile}\"")

                    if oldFile in self.curFiles:
                        self.curFiles[newFile] = self.curFiles[oldFile]
                    else:
                        self.curFiles[newFile] = uuid4().hex

                    continue

                # Markdown file
                r = search("^(\d+)\t(\d+)\t(.*\.md)$", rawResultLine)

                if r:
                    lineAddCount = r.group(1)
                    lineDelCount = r.group(2)
                    curFile = r.group(3).strip().replace("\"", "")

                    if not curFile in self.curFiles:
                        self.curFiles[curFile] = uuid4().hex

                    self.summary.append([
                        self.curRepo, self.curCommit,
                        self.curAuthor, self.curDate, self.curFiles[curFile],
                        curFile, lineAddCount, lineDelCount, "lines"])

                    print("MD: ", curFile,)

                    continue

                # Binary file
                r = search("^(.*) *\| Bin (\d+) -\> (\d+) bytes$",
                           rawResultLine)

                if r:
                    curFile = r.group(1).strip()
                    bytesFrom = r.group(2)
                    bytesTo = r.group(3).strip().replace("\"", "")

                    if not curFile in self.curFiles:
                        self.curFiles[curFile] = uuid4().hex

                    self.summary.append([
                        self.curRepo, self.curCommit,
                        self.curAuthor, self.curDate, self.curFiles[curFile],
                        curFile, bytesFrom, bytesTo, "bytes"])

                    print("BIN: ", curFile,)

                    continue

    def save(self):
        headers = ["Repo", "Commit", "Author", "Date", "File_Id",
                   "File", "Dat_1", "Dat2", "Type"]
        pd.DataFrame(self.summary, columns=headers).to_csv(self.outputFileName, sep="\t")


if __name__ == "__main__":
    interpreter = GithistInterpreter(argv[1:])
    interpreter.parse()
    interpreter.save()
