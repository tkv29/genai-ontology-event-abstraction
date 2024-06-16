from django import forms
from GOEA.models import UploadedFiles

class UploadFilesForm(forms.ModelForm):
    class Meta:
        model = UploadedFiles
        fields = ['xes_file', 'owl_file', 'custom_ontology_used']

class APIKeyForm(forms.Form):
    key = forms.CharField(label='OpenAI API Key', max_length = 100)