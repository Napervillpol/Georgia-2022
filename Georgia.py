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
def get_candidate(xpath):
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
    df.insert(5, 'Total ', df['Absentee by Mail Votes'].astype(int) + df['Election Day Votes'].astype(int)+df['Advanced Voting Votes'].astype(int)+df['Provisional Votes'].astype(int))

    return df

def assign_race(Dem,Rep,Dem_name,Rep_name):
       
    #Mail 
    Dem_mail = Dem[['Counties','Absentee by Mail Votes']]
    Dem_mail.columns=['County',Dem_name]

    Rep_mail = Rep[['Counties','Absentee by Mail Votes']]
    Rep_mail.columns=['County',Rep_name]
    mail = Dem_mail.merge(Rep_mail, on='County')
    calculations(mail,Dem_name,Rep_name)
   
    #Election day
    Dem_eday = Dem[['Counties','Election Day Votes']]
    Dem_eday.columns=['County',Dem_name]

    Rep_eday = Rep[['Counties','Election Day Votes']]
    Rep_eday.columns=['County',Rep_name]
    eday = Dem_eday.merge(Rep_eday, on='County')
    calculations(eday,Dem_name,Rep_name)

    #Advance
    Dem_advance = Dem[['Counties','Advanced Voting Votes']]
    Dem_advance.columns=['County',Dem_name]

    Rep_advance  = Rep[['Counties','Advanced Voting Votes']]
    Rep_advance.columns=['County',Rep_name]
    eday = Dem_eday.merge(Rep_eday, on='County')
    calculations(eday,Dem_name,Rep_name)

    #Provisonal
    Dem_prov= Dem[['Counties','Provisional Votes']]
    Dem_prov.columns=['County',Dem_name]

    Rep_prov = Rep[['Counties','Provisional Votes']]
    Rep_prov.columns=['County',Rep_name]
    prov = Dem_prov.merge(Rep_prov, on='County')
    calculations(prov,Dem_name,Rep_name)

     #Total
    Dem_total= Dem[['Counties','Votes']]
    Dem_total.columns=['County',Dem_name]

    Rep_total = Rep[['Counties','Votes']]
    Rep_total.columns=['County',Rep_name]
    total = Dem_total.merge(Rep_total, on='County')
    calculations(total,Dem_name,Rep_name)

    Race = race(mail,eday,prov,total)
    return Race;
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

Biden = get_candidate(".//Choice[@key='2']")

Trump = get_candidate(".//Choice[@key='1']")

#df = df.merge(df1, on='Counties')

df.to_csv('President.csv', index=False)
#df.to_json('runoff.json')

