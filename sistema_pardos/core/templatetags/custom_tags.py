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