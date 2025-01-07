from django.urls import path
from . import views

urlpatterns = [
    # URLs existentes
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('logout/', views.exit, name='exit'),
    path('register/', views.register, name='register'),
    
    # Gestión de Materiales
    path('materials/', views.material_list, name='material_list'),
    path('materials/add/', views.material_add, name='material_add'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),
    
    # Gestión de Colores
    path('colors/', views.color_list, name='color_list'),
    path('colors/add/', views.color_add, name='color_add'),
    path('colors/<int:pk>/edit/', views.color_edit, name='color_edit'),
    
    # Gestión de Tableros
    path('boards/', views.board_list, name='board_list'),
    path('boards/add/', views.board_add, name='board_add'),
    path('boards/<int:pk>/edit/', views.board_edit, name='board_edit'),
    path('boards/<int:pk>/delete/', views.board_delete, name='board_delete'),

     # Gestión de Producción
    path('production/', views.production_list, name='production_list'),
    path('production/add/', views.production_add, name='production_record_add'),
    path('production/<int:pk>/edit/', views.production_edit, name='production_record_edit'),
    path('production/<int:pk>/delete/', views.production_delete, name='production_record_delete'),
    path('production/quick-entry/', views.quick_production_entry, name='quick_production_entry'),
    path('production/export/csv/', views.export_production_csv, name='export_production_csv'),
    #path('production/export/pdf/', views.export_production_pdf, name='export_production_pdf'),
]