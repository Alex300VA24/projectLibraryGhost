from django import template
from django.utils.safestring import mark_safe

register = template.Library()

STATUS_MAPS = {
    'order': {
        'pending': {'classes': 'bg-yellow-100 text-yellow-700', 'icon': 'fa-regular fa-clock', 'label': 'Pendiente'},
        'ready': {'classes': 'bg-green-100 text-green-700', 'icon': 'fa-solid fa-box', 'label': 'Listo para entrega'},
        'completed': {'classes': 'bg-blue-100 text-blue-700', 'icon': 'fa-solid fa-check', 'label': 'Completado'},
        'cancelled': {'classes': 'bg-red-100 text-red-600', 'icon': 'fa-solid fa-xmark', 'label': 'Cancelado'},
    },
    'admin_order': {
        'Pendiente': {'classes': 'bg-yellow-100 text-yellow-700', 'icon': 'fa-regular fa-clock', 'label': 'Pendiente'},
        'Listo para entrega': {'classes': 'bg-green-100 text-green-700', 'icon': 'fa-solid fa-box', 'label': 'Listo para entrega'},
        'Completado': {'classes': 'bg-blue-100 text-blue-700', 'icon': 'fa-solid fa-check', 'label': 'Completado'},
        'Cancelado': {'classes': 'bg-red-100 text-red-600', 'icon': 'fa-solid fa-xmark', 'label': 'Cancelado'},
    },
    'admin_venta': {
        'Completada': {'classes': 'bg-green-100 text-green-700', 'icon': 'fa-solid fa-check', 'label': 'Completada'},
        'Pendiente': {'classes': 'bg-yellow-100 text-yellow-700', 'icon': 'fa-regular fa-clock', 'label': 'Pendiente'},
        'Cancelada': {'classes': 'bg-red-100 text-red-600', 'icon': 'fa-solid fa-xmark', 'label': 'Cancelada'},
    },
}

STATUS_ICONS = {
    'pending': 'fa-regular fa-clock',
    'ready': 'fa-solid fa-box',
    'completed': 'fa-solid fa-check',
    'cancelled': 'fa-solid fa-xmark',
    'Pendiente': 'fa-regular fa-clock',
    'Listo para entrega': 'fa-solid fa-box',
    'Completado': 'fa-solid fa-check',
    'Cancelado': 'fa-solid fa-xmark',
    'Completada': 'fa-solid fa-check',
    'Cancelada': 'fa-solid fa-xmark',
}

STATUS_LABELS = {
    'pending': 'Pendiente',
    'ready': 'Listo para entrega',
    'completed': 'Completado',
    'cancelled': 'Cancelado',
}

@register.filter
def badge_class(status, map_type='order'):
    m = STATUS_MAPS.get(map_type, STATUS_MAPS['order'])
    entry = m.get(status)
    if entry:
        return entry['classes']
    return 'bg-red-100 text-red-600'


@register.filter
def badge_icon(status, map_type='order'):
    m = STATUS_MAPS.get(map_type, STATUS_MAPS['order'])
    entry = m.get(status)
    if entry:
        return entry['icon']
    return STATUS_ICONS.get(status, 'fa-solid fa-circle')


@register.filter
def badge_label(status, map_type='order'):
    m = STATUS_MAPS.get(map_type, STATUS_MAPS['order'])
    entry = m.get(status)
    if entry:
        return entry['label']
    return STATUS_LABELS.get(status, status)


@register.simple_tag
def status_badge(status, map_type='order', extra_classes=''):
    m = STATUS_MAPS.get(map_type, STATUS_MAPS['order'])
    entry = m.get(status)
    if not entry:
        entry = {'classes': 'bg-red-100 text-red-600', 'icon': 'fa-solid fa-circle', 'label': status}
    return mark_safe(
        f'<span class="badge {entry["classes"]} {extra_classes}" data-status="{status}">'
        f'<span class="cb-icon" style="display:none"><i class="{entry["icon"]}"></i> </span>{entry["label"]}'
        f'</span>'
    )
