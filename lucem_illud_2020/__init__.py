import os
#For Windows
if os.name == 'nt':
    os.environ['JAVAHOME'] =  "C:/Program Files/Java/jdk1.8.0_161/bin/java.exe"

#gensim uses a couple of deprecated features
#we can't do anything about them so lets ignore them
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


from .data_dirs  import *
from .downloaders import *
from .loaders import *
from .visualizers import *
from .proccessing import *
from .cartoons import *
from .metrics import *
from .bayesian import *

from .info_extract import *


import requests
import re
import pkg_resources

_setupURL = 'https://raw.githubusercontent.com/Computational-Content-Analysis-2020/lucem_illud_2020/master/setup.py'

def _checkCurrentVersion():
    r = requests.get(_setupURL, timeout=0.5)
    serverVersion = re.search(r'versionString = \'(.+)\'', r.text).group(1)
    localVersion = pkg_resources.get_distribution('lucem_illud_2020').version
    if serverVersion != serverVersion:
        print('lucem_illud is out of date, please update')
        print('pip install -U git+git://github.com/Computational-Content-Analysis-2020/lucem_illud_2020.git')

try:
    checkCurrentVersion()
except:
    pass
