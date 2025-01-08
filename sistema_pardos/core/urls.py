from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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

    # Orders
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    path('orders/<int:pk>/measurements/', views.order_measurements, name='order_measurements'),

     # Gestión de Producción
    path('production/', views.production_list, name='production_list'),
    path('production/add/', views.production_add, name='production_record_add'),
    path('production/<int:pk>/edit/', views.production_edit, name='production_record_edit'),
    path('production/<int:pk>/delete/', views.production_delete, name='production_record_delete'),
    path('production/quick-entry/', views.quick_production_entry, name='quick_production_entry'),
    path('production/export/csv/', views.export_production_csv, name='export_production_csv'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)