"""URL configuration for GOEA project."""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.APIKeyFormView.as_view(), name="api_key_page"),
    path("upload/", views.UploadPageView.as_view(), name="upload_page"),
    path("reset/", views.ResetApiKey.as_view(), name="reset_api_key"),
    path("extraction/", views.ExtractionPageView.as_view(), name="extraction_page"),
    path("result/", views.ResultPageView.as_view(), name="result_page"),
    path('download-xes/', views.DownloadPageView.as_view(), name='download_page'),
    path('admin/', admin.site.urls),
]
