from django import forms
from cards.models import Word, Meaning, Comment


class CreateForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['writing', 'old_writing', 'transcription', 'tags']


class MeaningForm(forms.Form):
    meaning = forms.CharField(required=True, max_length=500, min_length=1, strip=True)


class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)


class CommentUpdateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class CrossMeaningUpdateForm(forms.ModelForm):
    class Meta:
        model = Meaning
        fields = ['text']


class TagAddForm(forms.Form):
    new_tag = forms.CharField(required=True, max_length=500, min_length=1, strip=True)
