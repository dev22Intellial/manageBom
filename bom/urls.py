from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='bom_home'),
    path('upload/', views.upload_master_bom, name='upload_master_bom'),
    path('api/bom-data/<int:bom_file_id>/', views.get_bom_data, name='get_bom_data'),
    path('compare/<int:master_bom_id>/', views.compare_boms, name='compare_boms'),
    path('comparison-summary/', views.comparison_summary, name='comparison_summary'),
]
