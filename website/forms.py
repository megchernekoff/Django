from django import forms

class SeasonForm(forms.Form):
    season = forms.IntegerField(required=False)
    shuffle = forms.BooleanField(initial=False, required=False)
