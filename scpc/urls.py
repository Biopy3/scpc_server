from django.urls import path

from . import views

urlpatterns = [
  path('', views.homepage, name = 'homepage'),
  path('save_post/', views.save_post, name = 'save_post'),
  path('download_results/<uuid:access_code>', views.download_results, name = 'download_results'),
]