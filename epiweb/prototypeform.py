from django import forms

class ClassifyDocument(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label='Document')
