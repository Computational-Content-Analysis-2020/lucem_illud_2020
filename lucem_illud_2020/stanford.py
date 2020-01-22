# import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)
# warnings.filterwarnings("ignore", category=FutureWarning)

# from .info_extract import stanfordDir, parserModelsPath, modelPath

# import os
# import os.path
# import tempfile
# import subprocess
# import io
# import time
# import pandas

# import nltk
# from nltk.tag import StanfordNERTagger
# from nltk.tag import StanfordPOSTagger
# from nltk.parse import stanford
# from nltk.tokenize import word_tokenize
# from nltk.tree import Tree
# from nltk.draw.tree import TreeView
# from nltk.tokenize import sent_tokenize

# # NER
# nerClassifierPath = os.path.join(stanfordDir, 'ner', 'classifiers', 'english.all.3class.distsim.crf.ser.gz')

# nerJarPath = os.path.join(stanfordDir, 'ner', 'stanford-ner.jar')

# nerTagger = StanfordNERTagger(nerClassifierPath, nerJarPath)


# # Postagger
# postClassifierPath = os.path.join(stanfordDir, 'postagger', 'models', 'english-bidirectional-distsim.tagger')

# postJarPath = os.path.join(stanfordDir, 'postagger', 'stanford-postagger.jar')

# postTagger = StanfordPOSTagger(postClassifierPath, postJarPath)


# # Parser

# parserJarPath = os.path.join(stanfordDir, 'parser', 'stanford-parser.jar')

# parser = stanford.StanfordParser(parserJarPath, parserModelsPath, modelPath)

# depParser = stanford.StanfordDependencyParser(parserJarPath, parserModelsPath)

# # Core
# def openIE(target, memoryGigsUsage = 2):
#     if isinstance(target, list):
#         target = '\n'.join(target)
#     #setup the java targets

#     jarsDir = os.path.join(stanfordDir, 'core')

#     cp = [
#         os.path.join(jarsDir, 'stanford-corenlp-3.8.0.jar'),
#         os.path.join(jarsDir, 'stanford-corenlp-3.8.0-models.jar'),
#         os.path.join(jarsDir, 'CoreNLP-to-HTML.xsl'),
#         os.path.join(jarsDir, 'slf4j-api.jar'),
#         os.path.join(jarsDir, 'slf4j-simple.jar'),
#     ]
#     with tempfile.NamedTemporaryFile(mode = 'w', delete = False, dir = '.') as f:
#         #Core nlp requires a files, so we will make a temp one to pass to it
#         #This file should be deleted by the OS soon after it has been used
#         f.write(target)
#         f.seek(0)
#         print("Starting OpenIE run")
#         #If you know what these options do then you should mess with them on your own machine and not the shared server
#         sp = subprocess.run(['java', '-mx{}g'.format(memoryGigsUsage), '-cp', ':'.join(cp), 'edu.stanford.nlp.naturalli.OpenIE', '-threads', '1', f.name], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
#         #Live stderr is non-trivial so this is the best we can do
#         print(sp.stderr.decode('utf-8'))
#         retSting = sp.stdout.decode('utf-8')
#     #Making the DataFrame, again having to pass a fake file, yay POSIX I guess
#     with io.StringIO(retSting) as f:
#         df = pandas.read_csv(f, delimiter = '\t', names =['certainty', 'subject', 'verb', 'object'])
#     return df

# def startCoreServer(port = 16432, memoryGigsUsage = 2):

#     if 'HOST_IP' in os.environ:
#         ip = os.environ['HOST_IP']
#     else:
#         ip = 'localhost'

#     print("Starting server on http://{}:{} , please wait a few seconds".format(ip, port))

#     p = subprocess.Popen(['java', '-mx{}g'.format(memoryGigsUsage), '-cp', os.path.join(stanfordDir, 'core', '*'), 'edu.stanford.nlp.pipeline.StanfordCoreNLPServer','-port', "{}".format(port), '-timeout', '15000000', '-threads', '1'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
#     time.sleep(3)
#     try:
#         done = False
#         i = 0
#         direction = 2
#         while True:
#             s = "click Kernel -> Then Interupt to stop "
#             s += " " * i
#             if direction > 0:
#                 s += "(((っ･д･)っ"
#             elif direction < 0:
#                 s += "(･ω･｀)))"
#             else:
#                 s += "  (* ﾟДﾟ)"
#             s = s.ljust(70)
#             print(s, end = '\r')
#             if direction == 0:
#                 time.sleep(1)
#             else:
#                 time.sleep(.3)
#             i += direction
#             if i > 10:
#                 direction -= 1
#             elif i < 1:
#                 direction =+ 1
#     except KeyboardInterrupt:
#         print()
#         print("Exiting (ノ≧▽≦)ノ")
#     finally:
#         p.terminate()
