from django.shortcuts import render, redirect
from .models import Contestants, Season
from .forms import SeasonForm
import numpy as np
import sqlite3
import json
import pandas as pd


def get_conn(db):
    conn = sqlite3.connect(db)
    return conn


def get_table_info(db, table, num):
    conn = get_conn(db)
    meta_df = pd.DataFrame(conn.execute("""PRAGMA table_info({})""".format(table)).fetchall())
    col_list = meta_df[1].to_list()
    df = pd.DataFrame(conn.execute("""select * from {0} where season_id = {1}""".format(table, num)).fetchall(), columns=col_list)
    return df

def home(request):
    if request.method == 'POST':
        form = SeasonForm(request.POST)
        if form.is_valid():
            season = form.cleaned_data['season']
            shuffle = form.cleaned_data['shuffle']
            return redirect('/results/{0}/{1}/'.format(season, shuffle),
                            {'season':season, 'shuffle':shuffle})
        else:
            console.log('form is invalid')
    else:
        form = SeasonForm()
    return render(request, 'website/home.html', {'form':form})


def results(request, season, shuffle):
    if shuffle == 'False':
        shuffle = ''
    conn = get_conn('db.sqlite3')
    cont_df = get_table_info('db.sqlite3', 'website_contestants', season)
    seas_df = get_table_info('db.sqlite3', 'website_season', season)

    if shuffle:
        cont_df = cont_df.sample(frac=1)
    cont_list = cont_df['contestant'].tolist()
    age_list = cont_df['age'].tolist()
    hometown_list = cont_df['hometown'].tolist()
    cont_info = zip(cont_list, age_list, hometown_list)
    snum, sname, snprem = seas_df.iloc[0].values

    return render(request, 'website/results.html', {'cont_info':cont_info,
                                                    'snum':snum, 'sname':sname,
                                                    'snprem':snprem})

def games(request):
    if request.method == 'POST':
        form = SeasonForm(request.POST)
        if form.is_valid() :
            season = form.cleaned_data['season']
            season_num = season
            conn = get_conn('db.sqlite3')
            df = pd.DataFrame(conn.execute("""select * from website_contestants where season_id = {}""".format(season_num)).fetchall())
            cont_list = df[0].tolist()
            print(cont_list)
            np.random.shuffle(cont_list)
            print(cont_list)
            cont_num = np.arange(1, len(cont_list) + 1)
            zip_cont_list = zip(cont_list, cont_num)
            # cont_list.shuffle()

            return render(request, 'website/games.html', {"form":form, "cont_num": cont_num, "zip_cont_list":zip_cont_list, 'allowed':'yes'})

    else:
        form = SeasonForm()
        return render(request, 'website/games.html', {'form':form, 'allowed':'no'})
