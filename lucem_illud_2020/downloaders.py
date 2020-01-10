#All these packages need to be installed from pip
import requests #for http requests
import bs4 #called `beautifulsoup4`, an html parser
import pandas #gives us DataFrames
import docx #reading MS doc files, install as `python-docx`

#Stuff for pdfs
#Install as `pdfminer2`
import pdfminer.pdfinterp
import pdfminer.converter
import pdfminer.layout
import pdfminer.pdfpage

#These come with Python
import re #for regexs
import urllib.parse #For joining urls
import io #for making http requests look like files
import json #For Tumblr API responses
import os.path #For checking if files exist
import os #For making directories

def downloadIfNeeded(targetURL, outputFile, **openkwargs):
    if not os.path.isfile(outputFile):
        outputDir = os.path.dirname(outputFile)
        #This function is a more general os.mkdir()
        if len(outputDir) > 0:
            os.makedirs(outputDir, exist_ok = True)
        r = requests.get(targetURL, stream = True)
        #Using a closure like this is generally better than having to
        #remember to close the file. There are ways to make this function
        #work as a closure too
        with open(outputFile, 'wb') as f:
            f.write(r.content)
    return open(outputFile, **openkwargs)

def readPDF(pdfFile):
    #Based on code from http://stackoverflow.com/a/20905381/4955164
    #Using utf-8, if there are a bunch of random symbols try changing this
    codec = 'utf-8'
    rsrcmgr = pdfminer.pdfinterp.PDFResourceManager()
    retstr = io.StringIO()
    layoutParams = pdfminer.layout.LAParams()
    device = pdfminer.converter.TextConverter(rsrcmgr, retstr, laparams = layoutParams, codec = codec)
    #We need a device and an interpreter
    interpreter = pdfminer.pdfinterp.PDFPageInterpreter(rsrcmgr, device)
    password = ''
    maxpages = 0
    caching = True
    pagenos=set()
    for page in pdfminer.pdfpage.PDFPage.get_pages(pdfFile, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    device.close()
    returnedString = retstr.getvalue()
    retstr.close()
    return returnedString


#Putting a max in case the blog has millions of images
#The given max will be rounded up to the nearest multiple of 50
def tumblrImageScrape(blogName, maxImages = 200):
    #Restating this here so the function isn't dependent on any external variables
    tumblrAPItarget = 'http://{}.tumblr.com/api/read/json'

    #There are a bunch of possible locations for the photo url
    possiblePhotoSuffixes = [1280, 500, 400, 250, 100]

    #These are the pieces of information we will be gathering,
    #at the end we will convert this to a DataFrame.
    #There are a few other datums we could gather like the captions
    #you can read the Tumblr documentation to learn how to get them
    #https://www.tumblr.com/docs/en/api/v1
    postsData = {
        'id' : [],
        'photo-url' : [],
        'date' : [],
        'tags' : [],
        'photo-type' : []
    }

    #Tumblr limits us to a max of 50 posts per request
    for requestNum in range(maxImages // 50):
        requestParams = {
            'start' : requestNum * 50,
            'num' : 50,
            'type' : 'photo'
        }
        r = requests.get(tumblrAPItarget.format(blogName), params = requestParams)
        requestDict = json.loads(r.text[len('var tumblr_api_read = '):-2])
        for postDict in requestDict['posts']:
            #We are dealing with uncleaned data, we can't trust it.
            #Specifically, not all posts are guaranteed to have the fields we want
            try:
                postsData['id'].append(postDict['id'])
                postsData['date'].append(postDict['date'])
                postsData['tags'].append(postDict['tags'])
            except KeyError as e:
                raise KeyError("Post {} from {} is missing: {}".format(postDict['id'], blogName, e))

            foundSuffix = False
            for suffix in possiblePhotoSuffixes:
                try:
                    photoURL = postDict['photo-url-{}'.format(suffix)]
                    postsData['photo-url'].append(photoURL)
                    postsData['photo-type'].append(photoURL.split('.')[-1])
                    foundSuffix = True
                    break
                except KeyError:
                    pass
            if not foundSuffix:
                #Make sure your error messages are useful
                #You will be one of the users
                raise KeyError("Post {} from {} is missing a photo url".format(postDict['id'], blogName))

    return pandas.DataFrame(postsData)

def getTextFromWikiPage(targetURL, sourceParNum, sourceText):
    #Make a dict to store data before adding it to the DataFrame
    parsDict = {'source' : [], 'paragraph-number' : [], 'paragraph-text' : [], 'source-paragraph-number' : [],  'source-paragraph-text' : []}
    #Now we get the page
    r = requests.get(targetURL)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    #enumerating gives use the paragraph number
    for parNum, pTag in enumerate(soup.body.findAll('p')):
        #same regex as before
        parsDict['paragraph-text'].append(re.sub(r'\[\d+\]', '', pTag.text))
        parsDict['paragraph-number'].append(parNum)
        parsDict['source'].append(targetURL)
        parsDict['source-paragraph-number'].append(sourceParNum)
        parsDict['source-paragraph-text'].append(sourceText)
    return pandas.DataFrame(parsDict)

def getGithubFiles(target, maxFiles = 100):
    #We are setting a max so our examples don't take too long to run
    #For converting to a DataFrame
    releasesDict = {
        'name' : [], #The name of the file
        'text' : [], #The text of the file, watch out for binary files
        'path' : [], #The path in the git repo to the file
        'html_url' : [], #The url to see the file on Github
        'download_url' : [], #The url to download the file
    }

    #Get the directory information from Github
    r = requests.get(target)
    filesLst = json.loads(r.text)

    for fileDict in filesLst[:maxFiles]:
        #These are provided by the directory
        releasesDict['name'].append(fileDict['name'])
        releasesDict['path'].append(fileDict['path'])
        releasesDict['html_url'].append(fileDict['html_url'])
        releasesDict['download_url'].append(fileDict['download_url'])

        #We need to download the text though
        text = requests.get(fileDict['download_url']).text
        releasesDict['text'].append(text)

    return pandas.DataFrame(releasesDict)
