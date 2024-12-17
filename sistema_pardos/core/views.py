from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Sum, F, Q
from datetime import datetime, timedelta
from .models import MaterialType, Color, Board, Inventory
from .forms import MaterialTypeForm, ColorForm, BoardForm, InventoryMovementForm



def home(request):
    return render(request, 'core/home.html')

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
    total_m3 = sum(board.total_volume_m3 for board in boards)
    total_value = sum(board.stock * board.price_per_m2 * board.width * board.height for board in boards)
    low_stock_count = sum(1 for board in boards if board.needs_restock)
    
    # Obtener listas para filtros
    materials = MaterialType.objects.all()
    colors = Color.objects.filter(is_active=True)
    
    context = {
        'boards': boards,
        'materials': materials,
        'colors': colors,
        'total_m3': total_m3,
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