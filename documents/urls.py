

from django.urls import path
from . import views

urlpatterns = [
    path("", views.document_list, name="document-list"),
    path("upload/", views.document_upload, name="document-upload"),
    path("<int:document_id>/", views.document_detail, name="document-detail"),
    path("<int:document_id>/grants/", views.document_grants, name="document-grants"),
    path("<int:document_id>/download/",views.document_download,name="document-download",
),
]

