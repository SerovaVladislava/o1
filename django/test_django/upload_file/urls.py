from django.urls import path, re_path
from .views import UploadFileView, AuthUserView, CategoryUpdateView, KeywordUpdateView

app_name = "upload_file"

urlpatterns = [
    re_path(r'^upload-file/?$', UploadFileView.as_view(), name='upload_file'),
    re_path(r'^auth/?$', AuthUserView.as_view(), name='auth_user'),
    re_path(r'^categories/?$', CategoryUpdateView.as_view(), name='category_update'),
    re_path(r'^keywords/?$', KeywordUpdateView.as_view(), name='keyword_update'),
]