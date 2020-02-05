import sklearn #For generating some matrices
import pandas #For DataFrames
import numpy as np #For arrays
import matplotlib.pyplot as plt #For plotting
import seaborn #Makes the plots look nice
import IPython.display #For displaying images

import os #For looking through files
import os.path #For managing file paths
import re
import tarfile

import zipfile
import sys

from .proccessing import normalizeTokens, trainTestSplit, word_tokenize, sent_tokenize

dataDirectory = '../data'

def loadTextDirectory(targetDir, encoding = 'utf-8'):
    text = []
    fileName = []

    for file in (file for file in os.scandir(targetDir) if file.is_file() and not file.name.startswith('.')):
        with open(file.path, encoding = encoding) as f:
            text.append(f.read())
        fileName.append(file.name)
    return pandas.DataFrame({'text' : text}, index = fileName)

def loadDir(targetDir, category):
    allFileNames = os.listdir(targetDir)
    #We need to make them into useable paths and filter out hidden files
    filePaths = [os.path.join(targetDir, fname) for fname in allFileNames if fname[0] != '.']

    #The dict that will become the DataFrame
    senDict = {
        'category' : [category] * len(filePaths),
        'filePath' : [],
        'text' : [],
    }

    for fPath in filePaths:
        with open(fPath) as f:
            senDict['text'].append(f.read())
            senDict['filePath'].append(fPath)

    return pandas.DataFrame(senDict)


def _loadEmailZip(targetFile, category):
    # regex for stripping out the leading "Subject:" and any spaces after it
    subject_regex = re.compile(r"^Subject:\s+")

    #The dict that will become the DataFrame
    emailDict = {
        'category' : [],
        'text' : [],
    }
    with tarfile.open(targetFile) as tar:
        for tarinfo in tar.getmembers():
            if tarinfo.isreg():
                with tar.extractfile(tarinfo) as f:
                    s = f.read().decode('latin1', 'surrogateescape')
                    for line in s.split('\n'):
                        if line.startswith("Subject:"):
                            #Could also save the subject field
                            subject = subject_regex.sub("", line).strip()
                            emailDict['text'].append(subject)
    emailDict['category'] = [category] * len(emailDict['text'])
    return pandas.DataFrame(emailDict)

def generateVecs(df, sents = False):
    df['tokenized_text'] = df['text'].apply(lambda x: word_tokenize(x))
    df['normalized_text'] = df['tokenized_text'].apply(lambda x: normalizeTokens(x))

    if sents:
        df['tokenized_sents'] = df['text'].apply(lambda x: [word_tokenize(s) for s in sent_tokenize(x)])
        df['normalized_sents'] = df['tokenized_sents'].apply(lambda x: [normlizeTokens(s) for s in x])

    ngCountVectorizer = sklearn.feature_extraction.text.TfidfVectorizer(max_df=0.5, min_df=3, stop_words='english', norm='l2')
    newsgroupsVects = ngCountVectorizer.fit_transform([' '.join(l) for l in df['normalized_text']])
    df['vect'] = [np.array(v).flatten() for v in newsgroupsVects.todense()]
    return df

def loadNewsGroups(categories = ['comp.sys.mac.hardware', 'comp.windows.x', 'misc.forsale', 'rec.autos']):
    newsgroupsCategories = categories
    newsgroups = sklearn.datasets.fetch_20newsgroups(subset='train', data_home = dataDirectory)
    newsgroupsDF = pandas.DataFrame(columns = ['text', 'category', 'source_file'])

    for category in newsgroupsCategories:
        print("Loading data for: {}".format(category))
        ng = sklearn.datasets.fetch_20newsgroups(subset='train', categories = [category], remove=['headers', 'footers', 'quotes'], data_home = dataDirectory)
        newsgroupsDF = newsgroupsDF.append(pandas.DataFrame({'text' : ng.data, 'category' : [category] * len(ng.data), 'source_file' : ng.filenames}), ignore_index=True)

    print("Converting to vectors")
    return generateVecs(newsgroupsDF)

def loadSenateSmall():
    print("Loading senate data")
    senReleasesDF = pandas.read_csv(os.path.join(dataDirectory, "ObamaClintonReleases.csv"), index_col=0)
    senReleasesDF = senReleasesDF.dropna(axis=0, how='any')

    senReleasesDF['category'] = senReleasesDF['targetSenator']
    print("Converting to vectors")
    return generateVecs(senReleasesDF)

def loadSenateLarge():
    dataDir = os.path.join(dataDirectory, 'grimmerPressReleases')
    senReleasesDF = pandas.DataFrame()

    for senatorName in [d for d in os.listdir(dataDir) if d[0] != '.']:
        print("Loading senator: {}".format(senatorName))
        senPath = os.path.join(dataDir, senatorName)
        senReleasesDF = senReleasesDF.append(loadDir(senPath, senatorName), ignore_index = True)

    print("Converting to vectors")
    return generateVecs(senReleasesDF)

def loadSpam(holdBackFraction = .2):
    print("Loading Spam")
    spamDF = _loadEmailZip(os.path.join(dataDirectory,'Spam_Data/20021010_spam.tar.bz2'), 'spam')
    print("Loading Ham")
    spamDF = spamDF.append(_loadEmailZip(os.path.join(dataDirectory,'Spam_Data/20021010_hard_ham.tar.bz2'), 'not spam'), ignore_index= True)
    spamDF = spamDF.append(_loadEmailZip(os.path.join(dataDirectory,'Spam_Data/20021010_easy_ham.tar.bz2'), 'not spam'), ignore_index= True)
    spamDF['is_spam'] = [c == 'spam' for c in spamDF['category']]
    spamDF['binary'] = spamDF['is_spam']

    print("Converting to vectors")
    return generateVecs(spamDF)

def loadReddit(holdBackFraction = .2):
    print("Loading Reddit data")
    redditDf = pandas.read_csv(os.path.join(dataDirectory,'reddit.csv'))
    redditDf = redditDf.dropna()
    redditDf['category'] = [s.split(':')[0] for s in redditDf['subreddit']]
    print("Converting to vectors")
    return generateVecs(redditDf)


def loadDavies(address, corpus_style="text", num_files=10000):
    texts_raw = {}
    for file in os.listdir(address + "/"):
        if corpus_style in file:
            print(file)
            zfile = zipfile.ZipFile(address + "/" + file)
            for file in zfile.namelist():
                texts_raw[file] = []
                with zfile.open(file) as f:
                    for line in f:
                        texts_raw[file].append(line)

    tokenized_texts = {}
    for files in texts_raw:
        if len(tokenized_texts) > num_files:
            break
        texts = clean_raw_text(texts_raw[files][1:])
        for text in texts:
            txts = word_tokenize(movie)
            try:
                tokenized_texts[txts[0][2:]] = txts[1:]
            except IndexError:
                continue
    return tokenized_texts

def clean_raw_text(texts_raw):
    clean_texts = []
    for text in texts_raw:
        try:
            text = text.decode("utf-8")
            clean_text = text.replace(" \'m", "'m").replace(" \'ll", "'ll").replace(" \'re", "'re").replace(" \'s", "'s").replace(" \'re", "'re").replace(" n\'t", "n't").replace(" \'ve", "'ve").replace(" /'d", "'d")
            clean_texts.append(clean_text)
        except AttributeError:
            # print("ERROR CLEANING")
            # print(text)
            continue
        except UnicodeDecodeError:
            # print("Unicode Error, Skip")
            continue
    return clean_texts
