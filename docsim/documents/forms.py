# Copyright (C) 2013 Consumers Unified LLC
# Licensed under the GNU AGPL v3.0 - http://www.gnu.org/licenses/agpl.html

from django import forms

class FindSimilarForm(forms.Form):
    min_score = forms.FloatField(min_value=0.1, max_value=.999, required=False)
    max_results = forms.IntegerField(min_value=1, required=False)

class FindSimilarByIdForm(FindSimilarForm):
    id = forms.CharField()


class FindSimilarByTextForm(FindSimilarForm):
    text = forms.CharField()
