from dataclasses import fields
import json
from tkinter.font import Font
from django.forms import DurationField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout
from django.urls import reverse
from openpyxl import Workbook
from prompt_toolkit import HTML
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import ExpressionWrapper
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Sum, F, Count
from datetime import datetime, timedelta
from .models import MaterialType, Color, Board, Inventory
from .forms import MaterialTypeForm, ColorForm, BoardForm, InventoryMovementForm
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Avg
from .models import ProductionRecord
from .forms import ProductionRecordForm, QuickProductionEntryForm
import csv
from django.http import HttpResponse
from django.template.loader import render_to_string
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order
from .forms import OrderForm
from django.template.loader import get_template


@login_required
def home(request):
    # Estadísticas generales
    total_products = Board.objects.filter(is_active=True).count()
    products_low_stock = Board.objects.filter(
        is_active=True,
        stock__lte=F('minimum_stock')
    ).count()
    total_value = Board.objects.filter(is_active=True).aggregate(
        total=Sum(F('stock') * F('price_per_m2') * F('width') * F('height'))
    )['total'] or Decimal('0')


    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    orders_stats = {
        'total_today': Order.objects.filter(created_at__date=today).count(),
        'total_month': Order.objects.filter(created_at__date__gte=this_month).count(),
        'pending': Order.objects.filter(status='pending').count(),
        'processing': Order.objects.filter(status__in=['processing', 'cutting', 'edge_banding']).count(),
        'completed': Order.objects.filter(status__in=['completed', 'delivered']).count(),
        'total_meters_month': Order.objects.filter(
            created_at__date__gte=this_month
        ).aggregate(
            total=Sum('total_meters')
        )['total'] or 0
    }

    # Datos para el gráfico
    last_days = 7
    orders_by_day = Order.objects.filter(
        created_at__date__gte=today - timedelta(days=last_days)
    ).values('created_at__date').annotate(
        count=Count('id'),
        meters=Sum('total_meters')
    ).order_by('created_at__date')

    chart_data = {
    'labels': json.dumps([d['created_at__date'].strftime('%d/%m') for d in orders_by_day]),
    'orders': json.dumps([d['count'] for d in orders_by_day]),
    'meters': json.dumps([float(d['meters'] or 0) for d in orders_by_day])
}
    
    # Filtros de pedidos
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    # Query base para pedidos
    recent_orders = Order.objects.all()
    
    # Aplicar filtros
    if status_filter:
        recent_orders = recent_orders.filter(status=status_filter)
    if date_filter:
        recent_orders = recent_orders.filter(created_at__date=date_filter)
    
    recent_orders = recent_orders.order_by('-created_at')[:10]  # Últimos 10 pedidos

    context = {
        'total_products': total_products,
        'products_low_stock': products_low_stock,
        'total_value': total_value,
        'recent_orders': recent_orders,
        'order_status_choices': Order.STATUS_CHOICES,
        'selected_status': status_filter,
        'selected_date': date_filter,
        'orders_stats': orders_stats,
        'chart_data': chart_data,
    }
    return render(request, 'core/home.html', context)

@login_required
def products(request):
    return render(request, 'core/products.html')

def exit(request):
    logout(request)
    return redirect('home')

def register(request):
    data = {
        'form' : CustomUserCreationForm()
    }
    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()

            user = authenticate(username = user_creation_form.cleaned_data['username'], password = user_creation_form.cleaned_data['password1'])
            login(request, user)

            return redirect('home')
    return render(request, 'registration/register.html', data)

# Nuevas vistas para gestión de materiales
@login_required
def material_list(request):
    materials = MaterialType.objects.all()
    return render(request, 'core/materials/list.html', {'materials': materials})

@login_required
def material_add(request):
    if request.method == 'POST':
        form = MaterialTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material agregado correctamente')
            return redirect('material_list')
    else:
        form = MaterialTypeForm()
    return render(request, 'core/materials/form.html', {'form': form, 'action': 'Agregar'})

@login_required
def material_edit(request, pk):
    material = get_object_or_404(MaterialType, pk=pk)
    if request.method == 'POST':
        form = MaterialTypeForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material actualizado correctamente')
            return redirect('material_list')
    else:
        form = MaterialTypeForm(instance=material)
    return render(request, 'core/materials/form.html', {'form': form, 'action': 'Editar'})

# Vistas para gestión de colores
@login_required
def color_list(request):
    colors = Color.objects.all()
    return render(request, 'core/colors/list.html', {'colors': colors})

@login_required
def color_add(request):
    if request.method == 'POST':
        form = ColorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Color agregado correctamente')
            return redirect('color_list')
    else:
        form = ColorForm()
    return render(request, 'core/colors/form.html', {'form': form, 'action': 'Agregar'})

@login_required
def color_edit(request, pk):
    color = get_object_or_404(Color, pk=pk)
    if request.method == 'POST':
        form = ColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            messages.success(request, 'Color actualizado correctamente')
            return redirect('color_list')
    else:
        form = ColorForm(instance=color)
    return render(request, 'core/colors/form.html', {'form': form, 'action': 'Editar'})

# Vistas para gestión de tableros
@login_required
def board_list(request):
    # Obtener filtros
    material_id = request.GET.get('material')
    color_id = request.GET.get('color')
    stock_status = request.GET.get('stock_status')
    
    # Consulta base
    boards = Board.objects.filter(is_active=True)
    
    # Aplicar filtros
    if material_id:
        boards = boards.filter(material_type_id=material_id)
    if color_id:
        boards = boards.filter(color_id=color_id)
    if stock_status == 'low':
        boards = boards.filter(stock__lte=F('minimum_stock'))
    elif stock_status == 'ok':
        boards = boards.filter(stock__gt=F('minimum_stock'))
    
    # Calcular estadísticas
    total_value = sum(board.stock * board.price_per_m2 * board.width * board.height for board in boards)
    low_stock_count = sum(1 for board in boards if board.needs_restock)
    
    # Obtener listas para filtros
    materials = MaterialType.objects.all()
    colors = Color.objects.filter(is_active=True)
    
    context = {
        'boards': boards,
        'materials': materials,
        'colors': colors,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
    }
    
    return render(request, 'core/boards/list.html', context)

@login_required
def board_add(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tablero agregado correctamente')
            return redirect('board_list')
    else:
        form = BoardForm()
    return render(request, 'core/boards/form.html', {'form': form, 'action': 'Agregar'})

@login_required
def board_edit(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tablero actualizado correctamente')
            return redirect('board_list')
    else:
        form = BoardForm(instance=board)
    return render(request, 'core/boards/form.html', {'form': form, 'action': 'Editar'})

# Vista para el dashboard con estadísticas
@login_required
def dashboard(request):
    total_products = Board.objects.filter(is_active=True).count()
    products_low_stock = Board.objects.filter(
        stock__lte=F('minimum_stock'),
        is_active=True
    ).count()
    total_value = Board.objects.filter(is_active=True).aggregate(
        total=Sum(F('stock') * F('price_per_m2') * F('width') * F('height')))['total'] or Decimal('0')

    context = {
        'total_products': total_products,
        'products_low_stock': products_low_stock,
        'total_value': total_value
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def board_delete(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        board.is_active = False  
        board.save()
        messages.success(request, 'Tablero eliminado correctamente')
        return redirect('board_list')
        
    return render(request, 'core/boards/delete_confirm.html', {'board': board})



def get_daily_stats():
    today = timezone.now().date()
    records = ProductionRecord.objects.filter(date=today)
    
    return {
        'total_meters': records.aggregate(Sum('meters_cut'))['meters_cut__sum'] or 0,
        'total_pieces': records.aggregate(Sum('pieces_cut'))['pieces_cut__sum'] or 0,
        'total_edges': records.aggregate(Sum('edges_applied'))['edges_applied__sum'] or 0,
        'avg_waste': records.aggregate(Avg('waste_percentage'))['waste_percentage__avg'] or 0,
    }

@login_required
def production_list(request):
    today = timezone.now().date()
    production_records = ProductionRecord.objects.filter(date=today)
    daily_stats = get_daily_stats()
    quick_form = QuickProductionEntryForm()

    context = {
        'production_records': production_records,
        'daily_stats': daily_stats,
        'quick_form': quick_form,
    }
    return render(request, 'production/production_list.html', context)

@login_required
def production_add(request):
    if request.method == 'POST':
        form = ProductionRecordForm(request.POST)
        if form.is_valid():
            production_record = form.save(commit=False)
            production_record.operator = request.user 
            production_record.date = timezone.now().date()
            production_record.save()
            messages.success(request, 'Registro de producción creado exitosamente.')
            return redirect('production_list')
    else:
        form = ProductionRecordForm()  
    
    return render(request, 'production/production_form.html', {'form': form, 'title': 'Nuevo Registro'})

@login_required
def production_edit(request, pk):
    production_record = get_object_or_404(ProductionRecord, pk=pk)
    
    if request.method == 'POST':
        form = ProductionRecordForm(request.POST, instance=production_record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro de producción actualizado exitosamente.')
            return redirect('production_list')
    else:
        form = ProductionRecordForm(instance=production_record)
    
    return render(request, 'production/production_form.html', {'form': form, 'title': 'Editar Registro'})

@login_required
def production_delete(request, pk):
    production_record = get_object_or_404(ProductionRecord, pk=pk)
    production_record.delete()
    messages.success(request, 'Registro de producción eliminado exitosamente.')
    return redirect('production_list')

@login_required
def quick_production_entry(request):
    if request.method == 'POST':
        form = QuickProductionEntryForm(request.POST)
        if form.is_valid():
            production_record = form.save(commit=False)
            production_record.operator = request.user
            production_record.date = timezone.now().date()
            production_record.start_time = timezone.now().time()
            production_record.end_time = timezone.now().time()
            production_record.save()
            messages.success(request, 'Registro rápido creado exitosamente.')
    return redirect('production_list')



import csv
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import datetime

@login_required
def export_production_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="produccion_{}.csv"'.format(
        datetime.now().strftime('%Y%m%d_%H%M%S')
    )
    
    # Crear el escritor CSV
    writer = csv.writer(response)
    # Escribir encabezados
    writer.writerow(['Operador', 'Fecha', 'Hora Inicio', 'Hora Fin', 
                    'Metros Cortados', 'Piezas', 'Metros de Canto', 'Desperdicio'])
    
    # Obtener registros
    records = ProductionRecord.objects.all().order_by('-date', '-start_time')
    
    # Escribir datos
    for record in records:
        writer.writerow([
            record.operator.get_full_name(),
            record.date,
            record.start_time,
            record.end_time,
            record.meters_cut,
            record.pieces_cut,
            record.edges_applied or '-',
            f"{record.waste_percentage}%"
        ])
    
    return response

@login_required
def export_production_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="produccion_{}.pdf"'.format(
        datetime.now().strftime('%Y%m%d_%H%M%S')
    )

    # Obtener registros
    records = ProductionRecord.objects.all().order_by('-date', '-start_time')
    
    html_string = render_to_string('production/production_pdf.html', {
        'records': records,
        'current_date': datetime.now()
    })
    
    from weasyprint import HTML
    HTML(string=html_string).write_pdf(response)
    
    return response



@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.save()
            messages.success(request, 'Pedido creado exitosamente.')
            if 'measurements' in request.POST:
                return redirect('order_measurements', pk=order.pk)
            return redirect('home')  # Redirige al inicio por defecto
    else:
        form = OrderForm()
    
    return render(request, 'core/orders/form.html', {
        'form': form,
        'title': 'Nuevo Pedido'
    })

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not (request.user.is_staff or order.customer == request.user):
        messages.error(request, 'No tiene permiso para ver este pedido.')
        return redirect('home')
    
    return render(request, 'core/orders/detail.html', {
        'order': order,
        'order_status_choices': Order.STATUS_CHOICES
    })



@login_required
def order_update_status(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('home')
        
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.get_status_display()
            order.status = new_status
            order.save()
            
            messages.success(
                request, 
                f'Estado del pedido actualizado de "{old_status}" a "{order.get_status_display()}".'
            )
        else:
            messages.error(request, 'Estado inválido.')
            
    return redirect('order_detail', pk=pk)


@login_required
def order_measurements(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            measurements = data.get('measurements', [])
            
            # Validar medidas
            if not measurements:
                return JsonResponse({'success': False, 'error': 'No hay medidas'})
            
            for measurement in measurements:
                if not all(key in measurement for key in ['largo', 'ancho', 'cantidad']):
                    return JsonResponse({'success': False, 'error': 'Datos incompletos'})
                
                if measurement['largo'] <= 0 or measurement['ancho'] <= 0 or measurement['cantidad'] <= 0:
                    return JsonResponse({'success': False, 'error': 'Valores inválidos'})
            
            # Guardar medidas
            order.measurements = measurements
            order.save()
            
            messages.success(request, 'Medidas guardadas exitosamente.')
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('home')  # Cambiar a home en lugar de order_detail
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'})
    
    return render(request, 'core/orders/measurements.html', {
        'order': order,
        'orderId': pk
    })



@login_required
def inventory_dashboard(request):
    # Obtener productos con problemas
    low_stock_products = Board.objects.filter(
        is_active=True,
        stock__lte=F('minimum_stock')
    )
    
    stale_products = Board.objects.filter(
        is_active=True,
        last_movement_date__lte=timezone.now() - timedelta(days=60)
    )
    
    # Estadísticas de rotación por color
    color_stats = Board.objects.values(
        'color__name'
    ).annotate(
        total_products=Count('id'),
        total_stock=Sum('stock'),
        avg_days_without_movement=Avg(
            ExpressionWrapper(
                timezone.now().date() - F('last_movement_date'),
                output_field=DurationField()
            )
        )
    ).order_by('-total_stock')

    context = {
        'low_stock_products': low_stock_products,
        'stale_products': stale_products,
        'color_stats': color_stats,
        'total_products': Board.objects.filter(is_active=True).count(),
        'total_value': Board.objects.filter(is_active=True).aggregate(
            total=Sum(F('stock') * F('price_per_m2') * F('width') * F('height'))
        )['total'] or 0
    }
    
    return render(request, 'inventory/dashboard.html', context)

@login_required
def production_dashboard(request):
    # Filtros de fecha
    today = timezone.now().date()
    date_from = request.GET.get('date_from', today.strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', today.strftime('%Y-%m-%d'))
    operator_id = request.GET.get('operator')

    # Query base
    productions = ProductionRecord.objects.all()
    
    # Aplicar filtros
    if date_from:
        productions = productions.filter(date__gte=date_from)
    if date_to:
        productions = productions.filter(date__lte=date_to)
    if operator_id:
        productions = productions.filter(operator_id=operator_id)

    # Estadísticas
    stats = productions.aggregate(
        total_meters=Sum('meters_cut'),
        total_pieces=Sum('pieces_cut'),
        total_edges=Sum('edges_applied'),
        avg_waste=Avg('waste_percentage')
    )

    # Estadísticas por operador
    operator_stats = productions.values(
        'operator__username',
        'operator__first_name',
        'operator__last_name'
    ).annotate(
        total_meters=Sum('meters_cut'),
        total_pieces=Sum('pieces_cut'),
        total_edges=Sum('edges_applied'),
        avg_waste=Avg('waste_percentage'),
        total_hours=Sum(
            ExpressionWrapper(
                F('end_time') - F('start_time'),
                output_field=fields.DurationField()
            )
        )
    )

    context = {
        'productions': productions,
        'stats': stats,
        'operator_stats': operator_stats,
        'operators': User.objects.filter(
            productionrecord__isnull=False
        ).distinct(),
        'date_from': date_from,
        'date_to': date_to,
        'selected_operator': operator_id
    }
    
    return render(request, 'production/dashboard.html', context)


@login_required
def production_reports(request):
    # Obtener fechas del filtro
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Por defecto último mes
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()

    # Obtener registros de producción
    productions = ProductionRecord.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('operator')

    # Estadísticas generales
    stats = productions.aggregate(
        total_meters=Sum('meters_cut'),
        total_pieces=Sum('pieces_cut'),
        total_edges=Sum('edges_applied'),
        avg_waste=Avg('waste_percentage')
    )

    # Producción por operador
    operator_production = productions.values(
        'operator__username',
        'operator__first_name',
        'operator__last_name'
    ).annotate(
        total_meters=Sum('meters_cut'),
        total_pieces=Sum('pieces_cut'),
        total_edges=Sum('edges_applied'),
        avg_waste=Avg('waste_percentage')
    )

    # Producción diaria
    daily_production = productions.values('date').annotate(
        total_meters=Sum('meters_cut'),
        total_pieces=Sum('pieces_cut')
    ).order_by('date')

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'stats': stats,
        'operator_production': operator_production,
        'daily_production': daily_production,
    }

    # Manejo de exportación
    if request.GET.get('export') == 'excel':
        return export_production_excel(request, context)
    elif request.GET.get('export') == 'pdf':
        return export_production_pdf(request, context)

    return render(request, 'reports/production.html', context)

def export_production_excel(request, context):
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte de Producción"

    # Encabezados
    headers = ['Fecha', 'Operador', 'Metros Cortados', 'Piezas', 'Cantos', 'Desperdicio (%)']
    ws.append(headers)

    # Datos
    productions = ProductionRecord.objects.filter(
        date__range=[context['start_date'], context['end_date']]
    ).select_related('operator')

    for prod in productions:
        ws.append([
            prod.date,
            prod.operator.get_full_name(),
            prod.meters_cut,
            prod.pieces_cut,
            prod.edges_applied or 0,
            prod.waste_percentage
        ])

    # Estilo
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")

    # Crear respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=produccion.xlsx'
    
    wb.save(response)
    return response

def export_production_pdf(request, context):
    template = get_template('reports/production_pdf.html')
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=produccion.pdf'
    
    HTML(string=html).write_pdf(response)
    return response