from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, F, Count


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
    def needs_restock(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock <= self.minimum_stock

    @property
    def days_without_movement(self):
        """Calcula días sin movimiento para control de rotación"""
        from django.utils import timezone
        return (timezone.now().date() - self.last_movement_date).days
    


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
    

class Order(models.Model):
    """Modelo para los pedidos de clientes"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'En Proceso'),
        ('cutting', 'En Corte'),
        ('edge_banding', 'En Enchapado'),
        ('completed', 'Completado'),
        ('delivered', 'Entregado'),
    ]

    CUSTOMER_TYPE_CHOICES = [
        ('carpenter', 'Carpintero'),
        ('architect', 'Arquitecto'),
        ('customer', 'Cliente Final'),
    ]

    # Campos básicos
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Cliente")
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, verbose_name="Tipo de Cliente")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    
    # Campos de contacto
    carpentry_business = models.CharField(max_length=200, blank=True, verbose_name="Nombre del Negocio")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    address = models.TextField(blank=True, verbose_name="Dirección")
    
    # Campos de contenido
    image = models.ImageField(upload_to='orders/', null=True, blank=True, verbose_name="Imagen de Medidas")
    notes = models.TextField(blank=True, verbose_name="Notas")
    measurements = models.JSONField(null=True, blank=True, verbose_name="Medidas")
    
    # Campos calculados
    total_meters = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Total Metros")
    estimated_delivery = models.DateTimeField(null=True, blank=True, verbose_name="Entrega Estimada")
    
    # Campos de tiempo
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer.get_full_name()}"

    def calculate_total_meters(self):
        """Calcula el total de metros basado en las medidas"""
        if self.measurements:
            total = 0
            for item in self.measurements:
                largo = float(item.get('largo', 0))
                ancho = float(item.get('ancho', 0))
                cantidad = int(item.get('cantidad', 0))
                total += (largo * ancho * cantidad)
            return round(total, 2)
        return 0

    # En models.py, actualiza el método calculate_delivery_time en la clase Order
def calculate_delivery_time(self):
    """Calcula el tiempo estimado de entrega basado en medidas y carga actual"""
    if not self.measurements:
        return None

    # Calcular metros totales
    total_meters = self.calculate_total_meters()
    
    # Factores base actualizados
    BASE_SPEED = 20  # metros por hora
    SETUP_TIME = 0.5  # horas
    MIN_TIME = 1  # hora mínima
    
    # Factores de complejidad
    piece_count = sum(int(m.get('cantidad', 0)) for m in self.measurements)
    complexity_factor = 1.2 if piece_count > 10 else 1
    
    # Obtener órdenes en proceso y calcular carga
    current_orders = Order.objects.filter(
        status__in=['processing', 'cutting'],
        created_at__date=timezone.now().date()
    ).exclude(id=self.id)
    
    workload = current_orders.aggregate(
        total=Sum('total_meters')
    )['total'] or 0
    
    # Ajustar tiempo base según factores
    base_hours = max((total_meters / BASE_SPEED) + SETUP_TIME, MIN_TIME)
    workload_factor = 1 + (workload / 1000)  # Aumenta tiempo según carga
    
    estimated_hours = base_hours * complexity_factor * workload_factor
    
    return timezone.now() + timedelta(hours=estimated_hours)

    def save(self, *args, **kwargs):
        # Actualizar metros totales
        self.total_meters = self.calculate_total_meters()
        
        # Actualizar tiempo estimado de entrega
        if not self.estimated_delivery:
            self.estimated_delivery = self.calculate_delivery_time()

        # Manejar historial de estados
        if not self.pk or (
            self.pk and 
            Order.objects.filter(pk=self.pk).exists() and 
            Order.objects.get(pk=self.pk).status != self.status
        ):
            def save_history():
                OrderStatusHistory.objects.create(
                    order=self,
                    status=self.status,
                    created_by=getattr(self, '_current_user', None)
                )
            transaction.on_commit(save_history)
        
        super().save(*args, **kwargs)

def calculate_total_meters(self):
    """Calcula el total de metros basado en las medidas"""
    if self.measurements:
        total = 0
        for item in self.measurements:
            largo = float(item.get('largo', 0))
            ancho = float(item.get('ancho', 0))
            cantidad = int(item.get('cantidad', 0))
            total += (largo * ancho * cantidad)
        return round(total, 2)
    return 0

def save(self, *args, **kwargs):
    # Si es una instancia nueva o el estado ha cambiado
    if not self.pk or (
        self.pk and 
        Order.objects.filter(pk=self.pk).exists() and 
        Order.objects.get(pk=self.pk).status != self.status
    ):
        # Guardar el historial después de que el pedido se guarde
        def save_history():
            OrderStatusHistory.objects.create(
                order=self,
                status=self.status,
                created_by=getattr(self, '_current_user', None)
            )
            
        # Usar transaction.on_commit para asegurar que el historial se guarde
        # solo si la transacción del pedido es exitosa
        transaction.on_commit(save_history)
        
    super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(
        max_length=20, 
        choices=Order.STATUS_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']




class StockAlert(models.Model):
    """Modelo para alertas de inventario"""
    ALERT_TYPES = [
        ('low_stock', 'Stock Bajo'),
        ('no_movement', 'Sin Movimiento'),
        ('high_demand', 'Alta Demanda')
    ]
    
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        verbose_name="Tablero"
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        verbose_name="Tipo de Alerta"
    )
    message = models.TextField(verbose_name="Mensaje")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Alerta de Stock"
        verbose_name_plural = "Alertas de Stock"

    @classmethod
    def create_alerts(cls):
        """Genera alertas automáticamente basadas en las condiciones del inventario"""
        # Usar now() con zona horaria
        today = timezone.now()
        today_start = timezone.make_aware(datetime.combine(today.date(), datetime.min.time()))
        
        # Limpiar alertas antiguas
        cls.objects.filter(
            created_at__lt=today_start - timedelta(days=7)
        ).delete()
        
        # Alertas de stock bajo
        low_stock_boards = Board.objects.filter(
            is_active=True,
            stock__lte=F('minimum_stock')
        )
        for board in low_stock_boards:
            cls.objects.get_or_create(
                board=board,
                alert_type='low_stock',
                is_active=True,
                defaults={
                    'message': f'Stock bajo: {board.stock} unidades (mínimo: {board.minimum_stock})'
                }
            )

        # Alertas de inactividad
        no_movement_boards = Board.objects.filter(
            is_active=True,
            last_movement_date__lte=today.date() - timedelta(days=60)
        )
        for board in no_movement_boards:
            cls.objects.get_or_create(
                board=board,
                alert_type='no_movement',
                is_active=True,
                defaults={
                    'message': f'Sin movimiento por {board.days_without_movement} días'
                }
            )

        # Alertas de alta demanda
        week_threshold = 10
        high_demand_boards = Board.objects.filter(
            inventory__date__gte=today_start - timedelta(days=7)
        ).annotate(
            movement_count=Count('inventory')
        ).filter(
            movement_count__gte=week_threshold
        )
        
        for board in high_demand_boards:
            cls.objects.get_or_create(
                board=board,
                alert_type='high_demand',
                is_active=True,
                defaults={
                    'message': f'Alta demanda detectada en los últimos 7 días'
                }
            )

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.board}"

