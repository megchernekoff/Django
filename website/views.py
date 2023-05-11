from django.shortcuts import render, redirect
from .models import Contestants, Season
from .forms import SeasonForm, ResultForm
import numpy as np
import sqlite3
import json
import pandas as pd
from django.urls import resolve
import requests
from sklearn.utils import shuffle


def get_conn(db):
    conn = sqlite3.connect(db)
    return conn

def shuffle_list(list_a):
    list_a_2 = list_a.copy()
    np.random.shuffle(list_a_2)
    return list_a_2

# Returns a shuffled zipped list of contestants & their index
# and the dictionary of their correct elimination order
def get_contestants_info(db, season):
    conn = get_conn(db)
    df = pd.DataFrame(conn.execute("""select placement, contestant from website_contestants where season_id = {}""".format(season)).fetchall())
    place_list, cont_list = df[0].tolist(), df[1].tolist()
    order_dict = {}
    for cont in range(len(cont_list)):
        order_dict[place_list[cont]] = cont_list[cont]
    shuff_cont_list = shuffle_list(cont_list)
    # print("shuffle contestant list")
    # print(shuff_cont_list)
    # correct_num_order = []
    # for cont in cont_list:
    #     correct_num_order.append(shuff_cont_list.index(cont))
    # print('correct order list')
    # print(correct_num_order)
    zip_cont_list = zip(place_list, shuff_cont_list)
    return order_dict, zip_cont_list, shuff_cont_list


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

def games(request, season):
    if request.method == 'POST':
        first_form = SeasonForm(request.POST)
        if first_form.is_valid():
            season = first_form.cleaned_data['season']
            print(season)
            order_dict, zip_list, cont_list = get_contestants_info('db.sqlite3', season)
            context = {'first_form': first_form, 'abled':'yes'}
        if 'submitanswers' in request.POST:
            order_dict, zip_list, cont_list = get_contestants_info('db.sqlite3', season)
            elim_data = list(order_dict.values())
            second_form = ResultForm(zip_list, elim_data, request.POST)

            if second_form.is_valid():
                form_data = list(second_form.cleaned_data.values())
                results = zip(form_data, elim_data)
                if form_data == elim_data:
                    context = {
                            'first_form': first_form,
                            'second_form': second_form,
                            "results": results,
                            'give':'no',
                            'congrats':'yes'
                            }
                else:
                    context = {
                            'first_form': first_form,
                            'second_form': second_form,
                            "results": results,
                            'give':'no'
                            }
                # return render(request, 'website/temp.html', context)
                return render(request, 'website/games_v2.html', context)
        if 'giveup' in request.POST:
            order_dict, zip_list, cont_list = get_contestants_info('db.sqlite3', season)
            elim_data = list(order_dict.values())
            second_form = ResultForm(zip_list, elim_data, request.POST)
            if second_form.is_valid():
                form_data = list(second_form.cleaned_data.values())
                results = zip(form_data, elim_data)
                    # context = {
                    #         'first_form': first_form,
                    #         'second_form': second_form,
                    #         'give':'yes'
                    #         }
                return render(request, 'website/games_v2.html',
                                    {'first_form': first_form,
                                     'second_form': second_form,
                                     "results":results,
                                     'give':'yes'
                                    })

        return redirect('/games/{}/'.format(season), context)

    else:
        first_form = SeasonForm()
        order_dict, zip_list, cont_list = get_contestants_info('db.sqlite3', season)
        elim_data = list(order_dict.values())
        second_form = ResultForm(zip_list, elim_data)
        context = {
                    'first_form': first_form,
                    'second_form': second_form,
                    }
        return render(request, 'website/games_v2.html', context)

# def games(request):
#     if request.method == 'POST':
#         if 'startgame' in request.POST:
#             form = SeasonForm(request.POST)
#             if form.is_valid() :
#                 season = form.cleaned_data['season']
#                 # season_num = season
#                 return redirect('/games/{}/'.format(season), {'season':season})
#
#                 # return render(request, 'website/games.html', {"form":form, "cont_num": cont_num, "zip_cont_list":zip_cont_list, 'allowed':'yes'})
#         if 'submitanswer' in request.POST:
#             form = SeasonForm(request.POST)
#             # print(form)
#             s = request.POST.get('season')
#             # print(s)
#             current_url = request.build_absolute_uri()
#             return render(request, 'website/games.html', {'form':form})
#     else:
#         form = SeasonForm()
#         return render(request, 'website/games.html', {'form':form, 'allowed':'no'})
#
# def games_pick(request, season):
#     if request.method == 'POST':
#         form = SeasonForm(request.POST)
#         if form.is_valid():
#             season = form.cleaned_data['season']
#             order_dict, zip_list, cont_list = get_contestants_info('db.sqlite3', season)
#             # mform = ResultForm(zip_list)
#             return redirect('/games/{}/'.format(season),
#                             {'form':form, 'season':season, 'zip_list':zip_list,
#                             'cont_list':cont_list, 'allowed':'yes'})
#             # current_url = request.build_absolute_uri()
#         if 'submitanswer' in request.POST:
#             order_dict, zip_list, cont_list = get_contestants_info('db.sqlite3', season)
#             # place, cont = zip(*zip_list)
#             form = ResultForm(zip_list, request.POST)
#
#             for cont, other in zip_list:
#                 formy = request.POST.get(other)
#             return render(request, 'website/temp.html', {'form':form, 'season':season,
#                                                                 'zip_list':zip_list,
#                                                                 'cont_list':cont_list,
#                                                                 'allowed':'yes'})
#
#     else:
#         form = SeasonForm()
#         order_dict, zip_list, cont_list = get_contestants_info('db.sqlite3', season)
#         return render(request, 'website/games_pick.html', {'form':form,
#                                                            'season':season,
#                                                            'zip_list':zip_list,
#                                                            'cont_list':cont_list,
#                                                            'allowed':'yes'
#                                                            })
