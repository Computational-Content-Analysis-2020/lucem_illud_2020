from .github import makeStudentRepo, repoName

import argparse
import os.path
import os

def argumentParser():
    parser = argparse.ArgumentParser(description="Content Analysis 2018 helper")
    parser.add_argument("targetDir", default = '.', nargs = '?')
    parser.add_argument("--repoName", default = repoName, nargs = '?')
    return parser.parse_args()

def makeUser():
    args = argumentParser()
    makeStudentRepo()

if __name__ == "__main__":
    makeUser()
