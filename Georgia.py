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

def write_to_excel(race,race_name):
    writer = pd.ExcelWriter('GA_'+race_name+ '.xlsx', engine='xlsxwriter')

    race.mail.to_excel(writer,sheet_name="Mail",index=False)
    race.eday.to_excel(writer,sheet_name="Election Day",index=False)
    race.advance.to_excel(writer,sheet_name="Advance",index=False)
    race.prov.to_excel(writer,sheet_name="Provisonal",index=False)
    race.total.to_excel(writer,sheet_name="Total",index=False)

    writer.save()
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
        header.append(VoteType.attrib['name'])
        
        for County in VoteType:
            columns.append(County.attrib['votes'])

            if VoteType.attrib['name'] == "Election Day Votes":
                counties.append(County.attrib['name'])

        rows.append(columns)

    df = pd.DataFrame(rows)
    df = df.T
    df.columns = header


    df.insert(0, "Counties", counties)
    df.insert(5, 'Total', df['Absentee by Mail Votes'].astype(int) + df['Election Day Votes'].astype(int)+df['Advanced Voting Votes'].astype(int)+df['Provisional Votes'].astype(int))

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
    advance = Dem_advance.merge(Rep_advance, on='County')
    calculations(advance,Dem_name,Rep_name)

    #Provisonal
    Dem_prov= Dem[['Counties','Provisional Votes']]
    Dem_prov.columns=['County',Dem_name]

    Rep_prov = Rep[['Counties','Provisional Votes']]
    Rep_prov.columns=['County',Rep_name]
    prov = Dem_prov.merge(Rep_prov, on='County')
    calculations(prov,Dem_name,Rep_name)

     #Total
    Dem_total= Dem[['Counties','Total']]
    Dem_total.columns=['County',Dem_name]

    Rep_total = Rep[['Counties','Total']]
    Rep_total.columns=['County',Rep_name]
    total = Dem_total.merge(Rep_total, on='County')
    calculations(total,Dem_name,Rep_name)

    Race = race(mail,eday,advance,prov,total)
    return Race;

def calculations(df,Dem_name,Rep_name):
   
    df[Dem_name]=df[Dem_name].astype(str)
    df[Rep_name]=df[Rep_name].astype(str)
    
    df[Dem_name]=df[Dem_name].str.replace(',','')
    df[Rep_name]=df[Rep_name].str.replace(',','')

    df[Dem_name]=df[Dem_name].astype(int)
    df[Rep_name]=df[Rep_name].astype(int)
    
    df.insert(3, "Total", df[Dem_name]+df[Rep_name])
    df.insert(4, "Net Votes", df[Dem_name]-df[Rep_name])
    df.insert(5, Dem_name+" Pct", df[Dem_name]/(df[Dem_name]+df[Rep_name]))
    df.insert(6, Rep_name+" Pct", df[Rep_name]/(df[Dem_name]+df[Rep_name]))
    df.insert(7, "Margin",(df[Dem_name]/(df[Dem_name]+df[Rep_name])) -(df[Rep_name]/(df[Dem_name]+df[Rep_name])))

def calculate_shift(df_2022,df_2020):
     
     df_2022.mail.insert(8, "Pct Shift",df_2022.mail["Margin"]-df_2020.mail["Margin"])
     df_2022.mail.insert(9, "Turnout",df_2022.mail["Total"]/df_2020.mail["Total"])

     df_2022.eday.insert(8, "Pct Shift",df_2022.eday["Margin"]-df_2020.eday["Margin"])
     df_2022.eday.insert(9, "Turnout",df_2022.eday["Total"]/df_2020.eday["Total"])

     df_2022.advance.insert(8, "Pct Shift",df_2022.advance["Margin"]-df_2020.advance["Margin"])
     df_2022.advance.insert(9, "Turnout",df_2022.advance["Total"]/df_2020.advance["Total"])

     df_2022.prov.insert(8, "Pct Shift",df_2022.prov["Margin"]-df_2020.prov["Margin"])
     df_2022.prov.insert(9, "Turnout",df_2022.prov["Total"]/df_2020.prov["Total"])

     df_2022.total.insert(8, "Pct Shift",df_2022.total["Margin"]-df_2020.total["Margin"])
     df_2022.total.insert(9, "Turnout",df_2022.total["Total"]/df_2020.total["Total"])



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

President =assign_race(Biden,Trump,"Biden","Trump")


url = 'https://results.enr.clarityelections.com//GA//107556/275242/reports/detailxml.zip'

r = requests.get(url)

filename = url.split('/')[-1]  # this will take only -1 splitted part of the url

with open(filename, 'wb') as output_file:
    output_file.write(r.content)

zf = ZipFile('detailxml.zip', 'r')
zf.extractall()
zf.close()
tree = etree.parse('detail.xml')
root = tree.getroot()

Ossoff = get_candidate(".//Choice[@key='5']")
Perdue = get_candidate(".//Choice[@key='4']")

Senaterunoff =assign_race(Ossoff,Perdue,"Ossoff","Perdue")


write_to_excel(Senaterunoff,"Senaterunoff")
#df = df.merge(df1, on='Counties')

#df.to_csv('President.csv', index=False)
#df.to_json('runoff.json')

