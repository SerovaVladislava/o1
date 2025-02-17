from django.urls import path, re_path
from .views import EmailSendView

app_name = "email_send"

urlpatterns = [
    re_path(r'^send-email/?$', EmailSendView.as_view(), name='email_send_view'),
]