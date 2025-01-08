from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import MaterialType, Color, Board, Inventory, ProductionRecord
from django import forms
from .models import Order

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields= ['username', 'first_name', 'last_name','email', 'password1', 'password2']


class MaterialTypeForm(forms.ModelForm):
    class Meta:
        model = MaterialType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name', 'code', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_code(self):
        code = self.cleaned_data['code'].upper()
        if Color.objects.filter(code=code).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('Ya existe un color con este código.')
        return code

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['material_type', 'color', 'thickness', 'width', 'height', 
                 'price_per_m2', 'minimum_stock', 'is_active']
        widgets = {
            'material_type': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'thickness': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price_per_m2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('material_type')
        color = cleaned_data.get('color')
        thickness = cleaned_data.get('thickness')

        if all([material_type, color, thickness]):
            # Verificar si ya existe un tablero con estas características
            existing = Board.objects.filter(
                material_type=material_type,
                color=color,
                thickness=thickness
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise ValidationError(
                    'Ya existe un tablero con este material, color y espesor.'
                )
        return cleaned_data

class InventoryMovementForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['board', 'quantity', 'price', 'notes']
        widgets = {
            'board': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo tableros activos
        self.fields['board'].queryset = Board.objects.filter(is_active=True)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        board = self.cleaned_data.get('board')
        
        if not board:
            return quantity
            
        if self.instance.movement_type == 'EXIT' and quantity > board.stock:
            raise ValidationError(
                f'No hay suficiente stock. Stock actual: {board.stock}'
            )
            
        return quantity

class BatchEntryForm(forms.Form):
    """Formulario para entrada de múltiples tableros"""
    file = forms.FileField(
        label='Archivo Excel/CSV',
        help_text='Seleccione un archivo Excel o CSV con el listado de productos'
    )
    
class DateRangeForm(forms.Form):
    """Formulario para reportes con rango de fechas"""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha inicial'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha final'
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('La fecha inicial no puede ser posterior a la fecha final')
        
        return cleaned_data
    

class MaterialTypeForm(forms.ModelForm):
    class Meta:
        model = MaterialType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name', 'code', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['material_type', 'color', 'thickness', 'width', 'height', 
                 'price_per_m2', 'minimum_stock', 'is_active']
        widgets = {
            'material_type': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'thickness': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price_per_m2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class InventoryMovementForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['board', 'quantity', 'price', 'notes']
        widgets = {
            'board': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProductionRecordForm(forms.ModelForm):
    class Meta:
        model = ProductionRecord
        fields = ['start_time', 'end_time', 
                 'meters_cut', 'pieces_cut', 'edges_applied', 
                 'waste_percentage']  
        widgets = {
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control flatpickr-input time-input',
                'placeholder': 'Seleccione hora',
                'style': 'max-width: 200px;'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control flatpickr-input time-input',
                'placeholder': 'Seleccione hora',
                'style': 'max-width: 200px;'
            }),
            'meters_cut': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': 'Ingrese los metros cortados'
            }),
            'pieces_cut': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el número de piezas'
            }),
            'edges_applied': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': 'Ingrese los metros de canto aplicados'
            }),
            'waste_percentage': forms.NumberInput(attrs={
                'step': '0.01',
                'max': '100',
                'min': '0',
                'class': 'form-control',
                'placeholder': 'Ingrese el porcentaje de desperdicio'
            })
        }


class QuickProductionEntryForm(forms.ModelForm):
    class Meta:
        model = ProductionRecord
        fields = ['meters_cut', 'pieces_cut', 'waste_percentage']
        widgets = {
            'meters_cut': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Metros cortados',
                'class': 'form-control mb-2'
            }),
            'pieces_cut': forms.NumberInput(attrs={
                'placeholder': 'Número de piezas',
                'class': 'form-control mb-2'
            }),
            'waste_percentage': forms.NumberInput(attrs={
                'step': '0.01',
                'max': '100',
                'min': '0',
                'placeholder': 'Porcentaje de desperdicio',
                'class': 'form-control mb-2'
            })
        }



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer_type', 'carpentry_business', 'phone', 
            'address', 'notes', 'image'
        ]
        widgets = {
            'customer_type': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'toggleBusinessFields(this.value)'
            }),
            'carpentry_business': forms.TextInput(attrs={
                'class': 'form-control carpentry-field'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }