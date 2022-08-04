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


print('Download Starting...')

url = 'https://results.enr.clarityelections.com//GA//107556/275242/reports/detailxml.zip'

r = requests.get(url)

filename = url.split('/')[-1]  # this will take only -1 splitted part of the url

with open(filename, 'wb') as output_file:
    output_file.write(r.content)

print('Download Completed!!!')

zf = ZipFile('detailxml.zip', 'r')
zf.extractall()
zf.close()
tree = etree.parse('detail.xml')
root = tree.getroot()

df = get_candidate('Ossoff', ".//Choice[@key='5']")

df1 = get_candidate('Perdue', ".//Choice[@key='4']")

df = df.merge(df1, on='Counties')

#df.insert(3, "Margin", safediv(df['Levin'] - df['Haley'], df['Levin'] + df['Haley']))

df.to_csv('Output.csv', index=False)

file_name='OC_Voting_Precinct.geojson'


with open(file_name, 'r', encoding='utf-8') as f:
    data = json.load(f)

#with urlopen("https://gisservices.oakgov.com/arcgis/rest/services/Enterprise/EnterpriseAdminDataMapService/MapServer/7/query?outFields=*&where=1%3D1&f=geojson") as response:
#    source = response.read()

#data = json.loads(source)

i = 0
for features in data['features']:

    features['properties']['Levin'] = 0
    features['properties']['Haley'] = 0
    features['properties']['Margin']= 0
    for Precincts in df['Precinct']:

        if features['properties']['PrecinctName'] == Precincts:
            features['properties']['Levin'] = int(df['Levin'][i])
            features['properties']['Haley'] = int(df['Haley'][i])
            features['properties']['Margin'] = float(df['Margin'][i])
            #print(features['properties']['PrecinctName'])
        i = i+1
    i=0



#json_data = json.dumps(data)

with open('new_file.geojson', 'w') as f:
    json.dump(data, f, indent=2)
    print("The json file is created")


