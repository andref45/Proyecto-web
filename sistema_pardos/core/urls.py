from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # URLs Base y Autenticación
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('logout/', views.exit, name='exit'),
    path('register/', views.register, name='register'),

    # URLs Dashboard y Datos en tiempo real
    path('dashboard/realtime/', views.dashboard_realtime, name='dashboard_realtime'),
    path('dashboard/update-data/', views.update_dashboard_data, name='update_dashboard_data'),
    path('inventory/dashboard-data/', views.dashboard_data, name='dashboard_data'),
    path('production/dashboard/', views.production_dashboard, name='production_dashboard'),
    path('production/add/', views.production_add, name='production_add'),

    # URLs Inventario
    path('inventory/dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('inventory/movement-history/<int:board_id>/', views.material_movement_history, name='material_movement_history'),
    path('inventory/low-stock-alert/', views.low_stock_alert, name='low_stock_alert'),

    # URLs Materiales
    path('materials/', views.material_list, name='material_list'),
    path('materials/add/', views.material_add, name='material_add'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),

    # URLs Colores
    path('colors/', views.color_list, name='color_list'),
    path('colors/add/', views.color_add, name='color_add'),
    path('colors/<int:pk>/edit/', views.color_edit, name='color_edit'),

    # URLs Tableros
    path('boards/', views.board_list, name='board_list'),
    path('boards/add/', views.board_add, name='board_add'),
    path('boards/<int:pk>/edit/', views.board_edit, name='board_edit'),
    path('boards/<int:pk>/delete/', views.board_delete, name='board_delete'),

    # URLs Pedidos
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    path('orders/<int:pk>/measurements/', views.order_measurements, name='order_measurements'),
    path('orders/my-orders/', views.customer_orders, name='customer_orders'),
    path('orders/my-orders/<int:pk>/', views.customer_order_detail, name='customer_order_detail'),
    

    # URLs Producción
    path('production/', views.production_dashboard, name='production_list'),  
    path('production/add/', views.production_add, name='production_record_add'),
    path('production/<int:pk>/edit/', views.production_edit, name='production_record_edit'),
    path('production/<int:pk>/delete/', views.production_delete, name='production_record_delete'),
    path('production/quick-entry/', views.quick_production_entry, name='quick_production_entry'),
    path('production/export/csv/', views.export_production_csv, name='export_production_csv'),
    path('production/efficiency/', views.production_efficiency, name='production_efficiency'),

    # URLs Reportes y Métricas
    path('reports/board-rotation/', views.board_rotation_report, name='board_rotation_report'),
    path('operator-metrics/', views.operator_metrics, name='operator_metrics'),

    # URLs Alertas y Notificaciones
    path('alerts/update/', views.update_alerts, name='update_alerts'),
    path('get-notifications/', views.get_notifications, name='get_notifications'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)