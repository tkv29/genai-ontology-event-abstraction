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
        self.clear_upload_directory()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UploadFilesForm(request.POST, request.FILES)

        if form.is_valid():
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
            selected_depth = int(slider_value)
        else:
            selected_depth = event_abstractor.get_max_depth()

        
        context.update({
            "selected_depth": selected_depth,
            "ontology_string": event_abstractor.create_ontology_representation(selected_depth),
            "ontology_graph": event_abstractor.visualize_graph(selected_depth),
            "max_depth": event_abstractor.get_max_depth()
        })
        
        self.request.session["selected_depth"] = selected_depth

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
        selected_depth = request.session.get("selected_depth")
        event_abstractor.abstract(selected_depth)
        return redirect('result_page')

class ResultPageView(TemplateView):
    template_name = 'result_page.html'