from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import datetime



class MaterialType(models.Model):
    """Tipo de material (MDF, Aglomerado, etc)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Tipo de Material"
        verbose_name_plural = "Tipos de Material"
    
    def __str__(self):
        return self.name

class Color(models.Model):
    """Colores disponibles para los tableros"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colores"
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Board(models.Model):
    """Modelo para los tableros"""
    material_type = models.ForeignKey(
        MaterialType, 
        on_delete=models.PROTECT,
        verbose_name="Tipo de Material"
    )
    color = models.ForeignKey(
        Color, 
        on_delete=models.PROTECT,
        verbose_name="Color"
    )
    thickness = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Espesor en milímetros",
        verbose_name="Espesor"
    )
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Ancho en metros",
        verbose_name="Ancho"
    )
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Alto en metros",
        verbose_name="Alto"
    )
    price_per_m2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Precio por m²"
    )
    stock = models.IntegerField(
        default=0,
        verbose_name="Stock Actual"
    )
    minimum_stock = models.IntegerField(
        default=5,
        verbose_name="Stock Mínimo"
    )
    last_movement_date = models.DateField(
        auto_now=True,
        verbose_name="Último Movimiento"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    class Meta:
        verbose_name = "Tablero"
        verbose_name_plural = "Tableros"
        unique_together = ['material_type', 'color', 'thickness']
    
    def __str__(self):
        return f"{self.material_type} {self.color} {self.thickness}mm"
    
    @property
    def volume_m3(self):
        """Calcula el volumen en metros cúbicos"""
        return (self.width * self.height * self.thickness/1000)
    
    @property
    def total_volume_m3(self):
        """Calcula el volumen total del stock en metros cúbicos"""
        return self.volume_m3 * self.stock
    
    @property
    def days_without_movement(self):
        """Calcula días sin movimiento"""
        from django.utils import timezone
        return (timezone.now().date() - self.last_movement_date).days
    
    @property
    def needs_restock(self):
        return self.stock <= self.minimum_stock

class Inventory(models.Model):
    """Registro de movimientos de inventario"""
    ENTRY = 'ENTRY'
    EXIT = 'EXIT'
    MOVEMENT_TYPES = [
        (ENTRY, 'Entrada'),
        (EXIT, 'Salida'),
    ]
    
    board = models.ForeignKey(
        Board, 
        on_delete=models.PROTECT,
        verbose_name="Tablero"
    )
    movement_type = models.CharField(
        max_length=5, 
        choices=MOVEMENT_TYPES,
        verbose_name="Tipo de Movimiento"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        verbose_name="Creado por"
    )
    
    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.board} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        if self.movement_type == self.ENTRY:
            self.board.stock += self.quantity
        else:
            self.board.stock -= self.quantity
        
        self.board.last_movement_date = self.date
        self.board.save()
        super().save(*args, **kwargs)





class ProductionRecord(models.Model):
    operator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Operador"
    )
    date = models.DateField(
        "Fecha",
        auto_now_add=True
    )
    start_time = models.TimeField(
        "Hora inicio"
    )
    end_time = models.TimeField(
        "Hora fin"
    )
    meters_cut = models.DecimalField(
        "Metros cortados",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    pieces_cut = models.IntegerField(
        "Piezas cortadas",
        validators=[MinValueValidator(0)]
    )
    edges_applied = models.DecimalField(
        "Metros de canto aplicados",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    waste_percentage = models.DecimalField(
        "Porcentaje de desperdicio",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        verbose_name = "Registro de producción"
        verbose_name_plural = "Registros de producción"
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"Producción {self.date} - {self.operator.get_full_name()}"

    def get_duration(self):
        """Calcula la duración del turno"""
        if self.start_time and self.end_time:
            start = datetime.combine(self.date, self.start_time)
            end = datetime.combine(self.date, self.end_time)
            return end - start
        return None