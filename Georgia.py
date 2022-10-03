import requests
import json
import pandas as pd
from lxml import etree

from zipfile import ZipFile
from urllib.request import urlopen

def safediv(x,y):
    try:
        return x/y
    except ZeroDivisionError:
        return 0
class race:
    mail=[]
    eday=[]
    advance=[];
    prov=[]
    total=[]
    def __init__(self, mail,eday,advance,prov,total):
        self.mail=mail
        self.eday=eday
        self.advance=advance
        self.prov=prov
        self.total=total
def get_candidate(name, xpath):
    header = []
    rows = []
    counties = []

    for VoteType in root.find(xpath):

        columns = []
        header.append(VoteType.attrib['name']+' ' +name)
        
        for County in VoteType:
            columns.append(County.attrib['votes'])

            if VoteType.attrib['name'] == "Election Day Votes":
                counties.append(County.attrib['name'])

        rows.append(columns)

    df = pd.DataFrame(rows)
    df = df.T
    df.columns = header


    df.insert(0, "Counties", counties)
    df.insert(5, 'Total '+name, df['Absentee by Mail Votes '+name].astype(int) + df['Election Day Votes '+name].astype(int)+df['Advanced Voting Votes '+name].astype(int)+df['Provisional Votes '+name].astype(int))

    return df


url = 'https://results.enr.clarityelections.com//GA//105369/271927/reports/detailxml.zip'

r = requests.get(url)

filename = url.split('/')[-1]  # this will take only -1 splitted part of the url

with open(filename, 'wb') as output_file:
    output_file.write(r.content)

zf = ZipFile('detailxml.zip', 'r')
zf.extractall()
zf.close()
tree = etree.parse('detail.xml')
root = tree.getroot()

df = get_candidate('Biden', ".//Choice[@key='2']")

df1 = get_candidate('Trump', ".//Choice[@key='1']")

df = df.merge(df1, on='Counties')

df.to_csv('President.csv', index=False)
#df.to_json('runoff.json')

