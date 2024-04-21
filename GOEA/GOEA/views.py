from django.http import JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from .forms import UploadFilesForm
from .logic.event_abstractor import EventAbstractor

class UploadPageView(TemplateView):
    template_name = 'upload_page.html'

    def get(self, request):
        form = UploadFilesForm()
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
        
        context["selected_depth"] = selected_depth
        context["ontology_string"] = event_abstractor.create_ontology_representation()
        context["ontology_graph"] = event_abstractor.visualize_graph(selected_depth)
        context["max_depth"] = event_abstractor.get_max_depth()
        
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
        # event_abstractor = EventAbstractor.get_instance()
        # selected_depth = int(request.POST.get("slider_value"))
        # event_abstractor.visualize_graph(selected_depth)
        return redirect('result_page')

class ResultPageView(TemplateView):
    template_name = 'result_page.html'