from django import forms


class TypeAForm(forms.Form):
    deliverable = forms.CharField()
