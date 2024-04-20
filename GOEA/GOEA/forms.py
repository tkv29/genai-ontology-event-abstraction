from django import forms
from .models import UploadedFiles

class UploadFilesForm(forms.ModelForm):
    class Meta:
        model = UploadedFiles
        fields = ['xes_file', 'owl_file']