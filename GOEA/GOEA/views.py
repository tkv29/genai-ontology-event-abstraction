from django.http import JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from .forms import UploadFilesForm
from .logic.event_abstractor import EventAbstractor
from . import settings
import os
import shutil

class UploadPageView(TemplateView):
    template_name = 'upload_page.html'

    def get(self, request):
        form = UploadFilesForm()
        self.request.session.flush()
        self.clear_upload_directory()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UploadFilesForm(request.POST, request.FILES)

        if form.is_valid():
            self.request.session["custom_ontology_used"] = form.cleaned_data['custom_ontology_used']
            uploaded_files = form.save()
            xes_path = uploaded_files.xes_file_path
            owl_path = uploaded_files.owl_file_path
            EventAbstractor(xes_path=xes_path, owl_path=owl_path)

            return redirect('extraction_page')

        return render(request, self.template_name, {'form': form})

    def clear_upload_directory(self):
        directory = os.path.join(settings.BASE_DIR, 'media')
        print(directory)
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    

class ExtractionView(TemplateView):
    template_name = 'extraction_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_abstractor = EventAbstractor.get_instance()
        context["xes_html"] = event_abstractor.get_xes_df().to_html()
        
        slider_value = self.request.GET.get('slider_value')
        if slider_value:
            abstraction_level = int(slider_value)
        else:
            abstraction_level = 1

        
        context.update({
            "abstraction_level": abstraction_level,
            "ontology_string": event_abstractor.create_ontology_representation(abstraction_level),
            "ontology_graph": event_abstractor.visualize_graph(abstraction_level),
            "max_depth": event_abstractor.get_max_depth()
        })
        
        self.request.session["abstraction_level"] = abstraction_level

        return context
    
    def get(self, request, *args, **kwargs):
        """Return a JSON response with the current progress of the pipeline."""
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        if is_ajax:
            progress_information = {
                "progress": self.request.session.get("progress"),
                "status": self.request.session.get("status"),
            }
            return JsonResponse(progress_information)

        self.request.session["progress"] = 0
        self.request.session["status"] = None
        self.request.session.save()

        return super().get(request, *args, **kwargs)
    
    def post(self, request):
        event_abstractor = EventAbstractor.get_instance()
        target_abstraction_depth = request.session.get("abstraction_level")
        abstraction_df = event_abstractor.abstract(self, target_abstraction_depth)
        request.session["abstraction_table"] = abstraction_df.to_html()
        return redirect('result_page')

class ResultPageView(TemplateView):
    template_name = 'result_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["abstraction_table"] = self.request.session.get("abstraction_table")
        return context