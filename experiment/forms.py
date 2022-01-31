from django import forms


class TypeAForm(forms.Form):
    deliverable = forms.CharField()


class TypeBForm(forms.Form):
    commit_id = forms.CharField(disabled=True)
    order = forms.IntegerField()
