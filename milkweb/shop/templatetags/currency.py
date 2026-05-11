from django import template

register = template.Library()

@register.filter
def vnd(value):
    """Format số tiền sang dạng 1,234,567 ₫"""
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "0 ₫"

    return "{:,.0f} ₫".format(value)


@register.filter
def mul(value, arg):
    """Nhân hai giá trị (price * quantity)"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0