import os
import os.path
import zipfile
import io
import requests


#This is the date at the end of each of the zip files, e.g.
#the date in stanford-ner-2017-06-09.zip
stanfordVersion = '2017-06-09'

#This is the version numbers of the parser models, these
#are files in `stanford-parser-full-2017-06-09.zip`, e.g.
#stanford-parser-3.7.0-models.jar
parserVersion = '3.7.0'

#This is where the zip files were unzipped.Make sure to
#unzip into directories named after the zip files
#Don't just put all the files in `stanford-NLP`
stanfordDir = os.path.join('..', 'stanford-NLP')

#Parser model, there are a few for english and a couple of other languages as well
modelName = 'englishPCFG.ser.gz'

#We need to extract the model from the jar for NLTK to use it

#Source
parserModelsPath = os.path.join(stanfordDir, 'parser', 'stanford-parser-3.8.0-models.jar')

#Destination
modelPath = os.path.join(stanfordDir, 'parser', modelName)

download_urls = {
    'parser' : 'https://nlp.stanford.edu/software/stanford-parser-full-2017-06-09.zip',
    'ner' : 'https://nlp.stanford.edu/software/stanford-ner-2017-06-09.zip',
    'postagger' : 'https://nlp.stanford.edu/software/stanford-postagger-full-2017-06-09.zip',
    'core' : 'http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip'
}

def setupStanfordNLP():
    os.makedirs(stanfordDir,  exist_ok = True)
    print("Starting downloads, this will take 5-10 minutes")
    for i, (k, v) in enumerate(download_urls.items()):
        dlDir = os.path.join(stanfordDir, k)
        if os.path.isdir(dlDir):
            print("{} already exists, skipping download".format(dlDir))
            continue
        print("[{}%] Downloading {} from {}".format(i * 25, k, v))
        r = requests.get(v)

        print("[{}%] Downloaded {}, extracting to {}".format((i + 1) * 25 - 1, k, dlDir))
        z = zipfile.ZipFile(io.BytesIO(r.content))
        #os.makedirs(dlDir,  exist_ok = True)
        z.extractall(stanfordDir)
        os.rename(os.path.join(stanfordDir, z.namelist()[0]), dlDir)

        if k == 'parser':
            #The model files are stored in the jar, we need to extract them for nltk to use
            if not os.path.isfile(modelPath):
                with zipfile.ZipFile(parserModelsPath) as zf:
                    with open(modelPath, 'wb') as f:
                        f.write(zf.read('edu/stanford/nlp/models/lexparser/{}'.format(modelName)))

    print("[100%]Done setting up the Stanford NLP collection")
