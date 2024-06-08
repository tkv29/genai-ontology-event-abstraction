# Standard Library Imports
import os
import shutil
import traceback
import zipfile
from tempfile import NamedTemporaryFile

# Third-Party Imports
from django.http import FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, RedirectView, FormView

# Local Imports
from . import settings
from GOEA.forms import UploadFilesForm, APIKeyForm
from GOEA.logic import utils as u
from GOEA.logic.event_abstractor import EventAbstractor


class APIKeyFormView(FormView):
    template_name = 'api_login_page.html'
    form_class = APIKeyForm
    success_url = reverse_lazy('upload_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = APIKeyForm()
        return context
    
    def form_valid(self, form):
        os.environ['OPENAI_API_KEY'] = form.cleaned_data['key']
        return super().form_valid(form)

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
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')


class ExtractionPageView(TemplateView):
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
        custom_ontology_used = request.session.get("custom_ontology_used")
        try:
            abstraction_df = event_abstractor.abstract(self, target_abstraction_depth, custom_ontology_used)
        except Exception as e:
            return render(
                self.request,
                'error_page.html',
                {'type': type(e).__name__, 'error_traceback': traceback.format_exc()}
            )
        request.session["abstraction_table"] = abstraction_df.to_html()
        return redirect('result_page')


class ResultPageView(TemplateView):
    template_name = 'result_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["abstraction_table"] = self.request.session.get("abstraction_table")
        return context

class ResetApiKey(RedirectView):
    """View for resetting the API key."""

    url = reverse_lazy("upload_page")

    def get(self, request, *args, **kwargs):
        """Handle GET requests by deleting the API key from the environment and redirecting to the landing page."""
        try:
            del os.environ['OPENAI_API_KEY']
        except KeyError as e:
            return render(
                self.request,
                'error_page.html',
                {'type': type(e).__name__,'error_traceback': traceback.format_exc()}
            )

        return super().get(request, *args, **kwargs)

class DownloadPageView(View):
    def post(self, request, *args, **kwargs):
        event_abstractor = EventAbstractor.get_instance()
        files_to_download = []
        event_abstractor_df = event_abstractor.get_data().copy()
        xes_medication_path = u.dataframe_to_xes(df=event_abstractor_df, name="medication.xes", activity_key="medication")
        xes_normalized_path = u.dataframe_to_xes(df=event_abstractor_df, name="normalized_medication.xes", activity_key="normalized_medication")
        xes_abstracted_medication_path = u.dataframe_to_xes(df=event_abstractor_df, name="abstracted_medication.xes", activity_key="abstracted_medication")
             
        files_to_download.append(xes_medication_path)
        files_to_download.append(xes_normalized_path)
        files_to_download.append(xes_abstracted_medication_path)
        
        return self.zip_files_response(files_to_download)
    
    @staticmethod
    def zip_files_response(files_to_download):
        """Prepare a ZIP file for multiple files to download."""
        with NamedTemporaryFile(mode="w+b", suffix=".zip", delete=False) as temp_zip:
            with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files_to_download:
                    file_name = os.path.basename(file_path)
                    zipf.write(file_path, arcname=file_name)

            temp_zip.close()

            response = FileResponse(open(temp_zip.name, "rb"), as_attachment=True)
            response["Content-Disposition"] = 'attachment; filename="downloaded_files.zip"'

        return response