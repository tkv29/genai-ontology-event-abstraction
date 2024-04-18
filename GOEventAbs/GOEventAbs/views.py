import io
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from .forms import UploadFilesForm
from .logic.event_abstractor import EventAbstractor
import pm4py

class LandingPageView(TemplateView):
    template_name = 'landing_page.html'

class UploadPageView(TemplateView):
    template_name = 'upload_page.html'

    def get(self, request):
        form = UploadFilesForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UploadFilesForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_files = form.save()
            xes_file_path = uploaded_files.xes_file_path
            owl_file_path = uploaded_files.owl_file_path
            print("XES file path:", xes_file_path)
            print("OWL file path:", owl_file_path)
            df = pm4py.read_xes(xes_file_path)
            print(df)
            return redirect('next_page')

        return render(request, self.template_name, {'form': form})

class ExtractionView(TemplateView):
    template_name = 'index.html'

class ResultPageView(TemplateView):
    template_name = 'index.html'