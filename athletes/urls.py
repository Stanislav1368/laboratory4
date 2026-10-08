from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_athlete, name='add_athlete'),
    path('upload/', views.upload_file, name='upload_file'),
    path('list/', views.list_data, name='list_data'),
    path('edit/<int:pk>/', views.edit_athlete, name='edit_athlete'),
    path('delete/<int:pk>/', views.delete_athlete, name='delete_athlete'),
    path('search/', views.search_ajax, name='search_ajax'),
]
