import requests
import random
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from io import StringIO
import sqlite3
import numpy as np
import warnings
warnings.filterwarnings("ignore")

FILEPATH = "https://en.wikipedia.org/wiki/Survivor_(American_TV_series)"

def create_connection(db):
    conn = None
    try:
        print('here')
        conn = sqlite3.connect(db)
        return conn
    except Error as e:
        print(e)

    return conn

def create_tuples(df):
    # conn = create_connection('db.sqlite3')
    # cursor = conn.cursor()
    tuples_list = list(df.itertuples(index=False, name=None))
    # for tup in tuples_list:

    return tuples_list


def get_html(num):
    web = requests.get(FILEPATH)
    web_html = bs(web.content)
    table = web_html.find("table", {"class":'wikitable sortable'})
    df = pd.read_html(StringIO(str(table)))[0]
    season_name, season_loc, season_prem =  df.loc[df['Season'] == num,
                                               ['Subtitle', 'Location', 'Original tribes']].values.tolist()[0]
    website_str = table.find('a', text='{}'.format(num))['href']
    if website_str.startswith('http://'):
        req = requests.get(website_str)
    else:
        website_str = 'http://wikipedia.org' + website_str
        req = requests.get(website_str)
    html = bs(req.content)
    return html, season_name, season_loc, season_prem


def get_contestant_table(html):
    pot_cont_tables = html.select('table[class*="wikitable"]')
    for tab in pot_cont_tables:
        for col in tab.find_all('th'):
            if 'contestant' in col.text.strip('\n').lower():
                cont_table = tab
                return cont_table
    else:
        return('no contestant table')

def clean(aff_str, regex_str):
    cleaned = re.sub(re.compile(regex_str), '', aff_str)
    return cleaned

def remove_italics(cont_table, season_name, season_loc, season_prem):
    cont_table.find_all('caption')[-1].insert_after('<caption>{}</caption>'.format(season_loc))
    cont_table.find_all('caption')[-1].insert_after('<caption>{}</caption>'.format(season_prem))

    # Remove footnotes
    season_name = clean(season_name, '\[.+\]')
    season_prem = clean(season_prem, '\[.+\]')
    season_loc = clean(season_loc, '\[.+\]')
    cont_table = clean(str(cont_table), '\[.+\]')

    #Insert season premise and location into html
    cap_index = str(cont_table).index('</caption>') + len('</caption>')
    cont_table = str(cont_table)[:cap_index] + '<caption>{}</caption>'.format(season_prem) + str(cont_table)[cap_index:]
    cont_table = bs(str(cont_table)[:cap_index] + '<caption>{}</caption>'.format(season_loc) + str(cont_table)[cap_index:])

    cont_table_new = cont_table
    cont_table_body = cont_table_new.find_all('tbody')[0]

    # Remove italics from Contestants Names
    new_cont_table_body = bs(clean(str(cont_table_body), re.compile('<i>.+</i>')))
    new_html= bs(str(cont_table_new).replace(str(cont_table_body), str(new_cont_table_body)))
    return new_html, season_name, season_loc, season_prem

def get_clean_df(tab, snum, sname, snprem):
    df = pd.read_html(StringIO(str(tab)))[0]
    col_list  = [i + ' ' + j if j != i else i for i,j in df.columns]
    df.columns=col_list
    df.fillna(0, inplace=True)
    df.rename(columns={'From':"Hometown", "Main game Finish":"Finish Placement"}, inplace=True)
    df = df.loc[(df['Contestant'] != 0) & (df['Hometown'] != 0)]

    contest = df[['Contestant', 'Age', 'Hometown', 'Finish Placement']]
    contest['Hometown'] = contest['Hometown'].apply(lambda x: x.replace(',', ', '))
    contest['Season'] = snum
    seas = pd.DataFrame(data=[(snum, sname, snprem)], columns = ['Season', 'SeasonName', 'SeasonPremise'])
    return contest, seas

def main_function(num):
    html, season_name, season_loc, season_prem = get_html(num)
    cont_table = get_contestant_table(html)
    new_html, season_name, season_loc, season_prem = remove_italics(cont_table, season_name, season_loc, season_prem)
    new_cont_table = get_contestant_table(new_html)
    ct, st = get_clean_df(new_cont_table, num, season_name, season_prem)
    return ct, st


if __name__ == '__main__':
    # html, season_name, season_loc, season_prem = get_html(31)
    # contt = get_contestant_table(html)
    # new_html, season_name, season_loc, season_prem = remove_italics(contt, season_name, season_loc, season_prem)
    # new_cont_table = get_contestant_table(new_html)
    # ct, st = get_clean_df(new_cont_table, 31, season_name, season_prem)

## UNCOMMENT OUT WHEN FINISHED DEEP DIVE
    conn = create_connection('db.sqlite3')
    cursor = conn.cursor()
    iter = 0
    NUM = 1
    for NUM in range(1, 43):
        print(NUM)
        ct, st = main_function(NUM)
        ct_tuples = create_tuples(ct)
        st_tuples = create_tuples(st)
        for tup in st_tuples:
            cursor.execute("""INSERT INTO website_season VALUES {}""".format(tup))
        for tup in ct_tuples:
            tup = tuple([iter]) + tup
            cursor.execute("""INSERT INTO website_contestants VALUES {}""".format(tup))
            iter += 1

    conn.commit()
    conn.close()
