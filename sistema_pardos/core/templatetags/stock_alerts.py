from django import template
from core.models import StockAlert

register = template.Library()

@register.simple_tag
def get_stock_alerts():
    return StockAlert.objects.filter(is_active=True)