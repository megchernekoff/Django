from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
import sqlite3
from .models import Season


conn = sqlite3.connect('db.sqlite3')
mylist = conn.execute("""select season_id, season_name from website_season;""").fetchall()
TITLE_LIST = []
for item in mylist:
    TITLE_LIST.append('Season {}: {}'.format(item[0], item[1]))


class SeasonForm(forms.Form):
    # season = forms.ChoiceField(required=True,
    #                          widget=forms.Select(choices=TITLE_LIST))
    season = forms.IntegerField(required=True)
    shuffle = forms.BooleanField(initial=False, required=False)

    def check_error(self):
        season = self.cleaned_data.get('season')
        if season == '':
            raise ValidationError('Please enter a season')
        return season
