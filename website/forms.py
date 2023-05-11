from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
import sqlite3
from .models import Season


conn = sqlite3.connect('db.sqlite3')
mylist = conn.execute("""select season_id, season_name from website_season;""").fetchall()
TITLE_LIST = []
for item in mylist:
    TITLE_LIST.append((item[0], 'Season {}: {}'.format(item[0], item[1])))


class SeasonForm(forms.Form):
    season = forms.CharField(required=True, max_length = 100,
                             widget=forms.Select(choices=TITLE_LIST)
                             )
    shuffle = forms.BooleanField(initial=False, required=False)

    def check_error(self):
        season = self.cleaned_data.get('season')
        if season == '':
            raise ValidationError('Please enter a season')
        return season



class ResultForm(forms.Form):
    def __init__(self, zip_list, elim_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        place, cont = zip(*zip_list)
        choices_list = [(cont[i], cont[i]) for i in range(len(cont))]
        self.correct_values = elim_list
        for c in range(len(place)):
            placement = place[c]
            self.fields[placement] = forms.ChoiceField(widget = forms.Select(),
                                     choices= choices_list, initial=cont[c],required=False)

    def clean(self):
        cleaned_data = super().clean()
        n = 0
        for field_name, field_value in cleaned_data.items():
            if field_value != self.correct_values[n]:
                self.fields[field_name].widget.attrs['class'] = 'incorrect'
            else:
                self.fields[field_name].widget.attrs['class'] = 'correct'
            n += 1
