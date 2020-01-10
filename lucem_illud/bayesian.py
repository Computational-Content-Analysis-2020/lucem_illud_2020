import pandas as pd
import os
import subprocess

def make_TalkbankXML(df, fname, database='my_dataset',language='eng'):
    '''
    This function will transform pandas dataframe into TalkbankXML for Bayesian estimation of influence.

    df:  pandas dataframe of utterences, need four columns: "name", "tokens", "start", "end".
    ("start", "end" is the start_time, and end_time of a utterence)

    fname:  file name to save xml output
    database: (arbitrary) name of your database
    language: 'eng' is the default. (currently also support 'chinese')

    Important: All non-English tokens and names should be unicode.
    '''


    #format dataframe
    df = df[['name','tokens','start','end']]
    unit='s'
    df['start'] = df['start'].apply(pd.to_numeric)
    df['end'] = df['end'].apply(pd.to_numeric)
    df = df.dropna() # only allow non-missing data
    df = pd.DataFrame(sorted(df.values.tolist(),key=lambda x:x[2]),columns=df.columns) #sort by time

    #generate xml
    fname_short = fname
    if os.path.sep in fname:
        new_path = "."+os.path.sep+'data'+os.path.sep+fname.split(os.path.sep)[-1].split('.')[0]+os.path.sep
        fname_short = fname.split(os.path.sep)[-1].split(os.path.sep)[0]
    else:
        new_path = "."+os.path.sep+'data'+os.path.sep+fname.split('.')[0]+os.path.sep
    if not '.' in fname_short:
        fname_short+='.xml'
    else:
        fname_short = fname_short.split('.')[0]+'.xml'
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    with open(new_path+fname_short,'w') as fw:
        print ('<?xml version="1.0" encoding="UTF-8"?>\n',file=fw)
        print ('<CHAT from="%s">' % database,file=fw)

        #create person_ids
        person_id ={}
        for person in set(df['name'].values.tolist()):
            if not person in person_id: person_id[person] = len(person_id)+1

        #add participants
        print ('<Participants>',file=fw)
        for person in person_id:
            print ('<participant id="%s" name="%s" role="Adult" language="%s"/>' %(person,person,language),file=fw)
        print ('</Participants>\n',file=fw)

        #add utterences
        for row in df.values:
            print ('<u who="%s" uID="#%s">' % (row[0],person_id[row[0]]),file=fw)
            for word in row[1]:
                print ('''<w>%s</w>''' % word, file=fw)

            print ('''<media start="%s" end="%s" unit="%s"/>''' %(row[2],row[3],unit),file=fw)
            print ('''</u>''',file=fw)
            print ('''''', file=fw)
        print ("</CHAT>\n",file=fw)


    print ('New File saved to %s' % new_path+fname_short)
    return 0


def bec_run(output_fname, Vocab_size, language, sampling_time):
    subprocess.call(["python", "../data/Bayesian-echo/src/run_bec.py", output_fname,str(Vocab_size),language,str(int(sampling_time))])
