from django import template

register = template.Library()

@register.filter
def status_badge(status):
    status_colors = {
        'pending': 'warning',
        'processing': 'info',
        'cutting': 'primary',
        'edge_banding': 'secondary',
        'completed': 'success',
        'delivered': 'dark'
    }
    return status_colors.get(status, 'light')


@register.filter
def get_status_percentage(status):
    status_percentages = {
        'pending': 20,
        'processing': 40,
        'cutting': 60,
        'edge_banding': 80,
        'completed': 100,
        'delivered': 100
    }
    return status_percentages.get(status, 0)


@register.filter
def get_status_index(status):
    status_order = {
        'pending': 0,
        'processing': 1,
        'cutting': 1,
        'edge_banding': 1,
        'completed': 2,
        'delivered': 3
    }
    return status_order.get(status, -1)

@register.filter
def calculate_area(measurement):
    largo = float(measurement.get('largo', 0))
    ancho = float(measurement.get('ancho', 0))
    cantidad = int(measurement.get('cantidad', 0))
    return largo * ancho * cantidad


@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0
    


from django import template

register = template.Library()

@register.filter
def status_badge(status):
    """Devuelve la clase de badge para cada estado"""
    badges = {
        'pending': 'warning',
        'processing': 'primary',
        'cutting': 'info',
        'edge_banding': 'info',
        'completed': 'success',
        'delivered': 'secondary'
    }
    return badges.get(status, 'secondary')

@register.filter
def get_status_index(status):
    """Devuelve el índice del estado para la barra de progreso"""
    status_order = {
        'pending': 0,
        'processing': 1,
        'cutting': 1,
        'edge_banding': 1,
        'completed': 2,
        'delivered': 3
    }
    return status_order.get(status, -1)

@register.filter
def calculate_area(measurement):
    """Calcula el área de una medida"""
    try:
        return float(measurement['largo']) * float(measurement['ancho']) * int(measurement['cantidad'])
    except (KeyError, ValueError, TypeError):
        return 0