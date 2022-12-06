import requests
import json
import pandas as pd
from lxml import etree

from zipfile import ZipFile
from urllib.request import urlopen

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm

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
    df.insert(5, 'Total', df['Absentee by Mail Votes'].astype(int) + df['Election Day Votes'].astype(int)+df['Advance Voting Votes'].astype(int)+df['Provisional Votes'].astype(int))

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
    Dem_advance = Dem[['Counties','Advance Voting Votes']]
    Dem_advance.columns=['County',Dem_name]

    Rep_advance  = Rep[['Counties','Advance Voting Votes']]
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

def Statmodels(Previous_race,Current_race,Current_name,Title,w):
    
  
    
    plt.title(Title)
    plt.xlabel("Warnock General Pct")
    plt.ylabel("Warnock Runoff Pct")

    plt.scatter(Previous_race['Warnock Pct'],Current_race[Current_name],w)
   
  

    x = Previous_race['Warnock Pct']
    y = Current_race['Warnock Pct']
    z = w
    
 
    wls_model = sm.WLS(y,x,z)
    results = wls_model.fit()
    
    
    plt.plot(x,results.fittedvalues)
    
    xpoint = pd.DataFrame(x, columns=['Warnock Pct'])
    ypoint = pd.DataFrame(results.fittedvalues, columns=['expected'])
    newline = pd.merge(xpoint, ypoint, left_index=True, right_index=True)
    newline =newline.sort_values(by=['expected']).reset_index(drop=True)
    
    swing = (newline.iloc[0][1] - newline.iloc[0][0] + newline.iloc[-1][1] - newline.iloc[-1][0])
    print("{} swing: {:.1%}".format(Title,swing))
    x = np.linspace(0,1,5)
    y = x
   
    plt.grid()
    plt.plot(x, y, '-r', label='y=x+1')

    plt.show()

def reporting(xpath):
    header=[]
    pct_reporting=[]
    for Counties in root.find(xpath):
        header.append(Counties.attrib['name'])
        pct_reporting.append(Counties.attrib['precinctsReportingPercent'])
    df2 = pd.DataFrame( pct_reporting,columns=['precinctsReportingPercent'])

    df = pd.DataFrame(header,columns=['County'])
    df=df.join(df2, how='outer')
    return df
    
    

Warnock = pd.read_csv("Data/Warnock.csv")
Walker = pd.read_csv("Data/Walker.csv")
Senate =assign_race(Warnock,Walker,"Warnock","Walker")

url = "https://results.enr.clarityelections.com//GA//115465/314004/reports/detailxml.zip"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
r = requests.get(url,headers=headers) 
with open("detailxml.zip",'wb') as f:
    f.write(r.content)

filename = url.split('/')[-1]  # this will take only -1 splitted part of the url

with open(filename, 'wb') as output_file:
    output_file.write(r.content)
    
    zf = ZipFile('detailxml.zip', 'r')
    zf.extractall()
    zf.close()

tree = etree.parse('detail.xml')
root = tree.getroot()


Warnock_runoff = get_candidate(".//Choice[@key='2']")
Walker_runoff = get_candidate(".//Choice[@key='1']")



Senate_runoff =assign_race(Warnock_runoff,Walker_runoff,"Warnock","Walker")
calculate_shift(Senate_runoff,Senate)

reporting_precincts =reporting(".//Counties")
Senate_runoff.total=Senate_runoff.total.merge(reporting_precincts,on="County")
Senate.total=Senate.total.merge(reporting_precincts,on="County")

Mail_vote = pd.read_csv("Data/Mail.csv")
Advance_vote = pd.read_csv("Data/Advance.csv")

Senate_runoff.mail =Senate_runoff.mail.merge(Mail_vote,on="County")
Senate_runoff.advance =Senate_runoff.advance.merge(Advance_vote,on="County")

Senate_runoff.mail.insert(11,"Mail Remaining",Senate_runoff.mail['Mail']-Senate_runoff.mail['Total'])
Senate_runoff.mail.loc[Senate_runoff.mail['Mail Remaining'] < 0, 'Mail Remaining'] =0

Senate_runoff.advance.insert(11,"Advance Remaining",Senate_runoff.advance['Advance']-Senate_runoff.advance['Total'])
Senate_runoff.advance.loc[Senate_runoff.advance['Advance Remaining'] < 0, 'Advance Remaining'] =0

write_to_excel(Senate_runoff,"Senate_runoff")
#write_to_excel(Senate,"Senate")



Statmodels(Senate.total.loc[(Senate.total['precinctsReportingPercent']  =="100.00" )],Senate_runoff.total.loc[(Senate_runoff.total['precinctsReportingPercent']  =='100.00' )],"Warnock Pct","Total",Senate.total.loc[(Senate.total['precinctsReportingPercent']  =="100.00" )]['Total']/750)


