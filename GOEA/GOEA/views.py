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

class ResultPageView(TemplateView):
    template_name = 'index.html'