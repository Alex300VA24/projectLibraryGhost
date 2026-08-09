import json
import secrets
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from functools import wraps

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.accounts.models import Role, UserProfile
from apps.orders.models import Notification, Order, OrderHistory, OrderItem, OrderStatus
from apps.orders.services.email_service import send_order_ready_email
from apps.orders.services.notification_service import (
    create_notification,
    get_unread_count,
    mark_all_as_read,
    mark_as_read,
)
from apps.orders.services.order_service import OrderService, generate_boleta_code
from apps.orders.services.qr_service import generate_qr_base64 as _generate_qr_base64
from apps.products.models import Product, Category, ProductBatch
from payment_simulation.utils import build_simulation_absolute_uri
from .models import Expense
from library_ghostitzer.storage_backends import get_signed_url

User = get_user_model()


def _ean13_checksum(first_12_digits):
    digits = [int(d) for d in first_12_digits]
    odd_sum = sum(digits[::2])
    even_sum = sum(digits[1::2])
    return str((10 - ((odd_sum + even_sum * 3) % 10)) % 10)


def _normalize_barcode(value):
    return ''.join(ch for ch in str(value or '') if ch.isdigit())


def _generate_product_barcode(product):
    body = '775' + str(product.id).zfill(9)[-9:]
    return body + _ean13_checksum(body)


def _ensure_product_barcode(product):
    if product.codigo and product.codigo == _normalize_barcode(product.codigo) and len(product.codigo) == 13:
        return product.codigo
    product.codigo = _generate_product_barcode(product)
    product.save(update_fields=['codigo', 'updated_at'])
    return product.codigo


def _reduce_stock_fifo(product, quantity):
    if not product or quantity <= 0:
        return
    batches = product.batches.filter(quantity__gt=0).order_by('created_at')
    remaining = quantity
    for batch in batches:
        if remaining <= 0:
            break
        to_deduct = min(batch.quantity, remaining)
        batch.quantity -= to_deduct
        if to_deduct > 0:
            batch.is_locked = True
        batch.save()
        remaining -= to_deduct
    if remaining > 0:
        product.stock = max(0, product.stock - remaining)
        product.save(update_fields=['stock', 'updated_at'])


def _staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if hasattr(request.user, 'profile') and request.user.profile.must_change_password:
            return redirect('first_login_password_change')
        if not (request.user.is_staff or
                (hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.name in ('admin', 'employee'))):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('No tienes permiso para acceder a esta pagina.')
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    products = Product.objects.filter(is_available=True)[:8]
    return render(request, 'core/home.html', {'products': products})


def como_funciona(request):
    return render(request, 'core/como_funciona.html')


def contacto(request):
    return render(request, 'core/contacto.html')


@_staff_required
def dashboard(request):
    today = timezone.now().date()
    fresh_login = request.session.pop('fresh_login', False)
    context = {
        'total_orders': Order.objects.count(),
        'total_products': Product.objects.filter(is_available=True).count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'revenue_today': Order.objects.filter(
            created_at__date=today, status=OrderStatus.COMPLETED
        ).aggregate(total=Sum('total'))['total'] or 0,
        'fresh_login': fresh_login,
    }
    return render(request, 'core/admin/dashboard.html', context)


@csrf_exempt
@require_http_methods(['GET'])
@_staff_required
def api_dashboard_stats(request):
    today = timezone.localtime(timezone.now()).date()
    offset = int(request.GET.get('offset', 0))
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    month_start = today.replace(day=1)

    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    day_orders = Order.objects.filter(
        status=OrderStatus.COMPLETED,
        updated_at__range=(today_start, today_end),
    )
    ventas_hoy = day_orders.aggregate(t=Sum('total'))['t'] or 0
    gastos_hoy = Expense.objects.filter(date=today).aggregate(t=Sum('amount'))['t'] or 0

    dias_es = {0: 'Lun', 1: 'Mar', 2: 'Mié', 3: 'Jue', 4: 'Vie', 5: 'Sáb', 6: 'Dom'}
    chart = []
    week_total = 0
    for i in range(0, 7):
        day = monday + timedelta(days=i)
        day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
        day_end = timezone.make_aware(datetime.combine(day, datetime.max.time()))
        day_orders = Order.objects.filter(
            status=OrderStatus.COMPLETED,
            updated_at__range=(day_start, day_end),
        )
        day_count = day_orders.count()
        day_total = day_orders.aggregate(t=Sum('total'))['t'] or 0
        week_total += day_total
        chart.append({
            'label': dias_es[day.weekday()],
            'fecha': day.strftime('%d/%m'),
            'cantidad': day_count,
            'ventas': float(day_total),
            'isToday': day == today,
        })
    ventas_semana = week_total

    week_start_fmt = chart[0]['fecha'] + '/' + str(today.year)
    week_end_fmt = chart[6]['fecha'] + '/' + str(today.year)

    week_start = today - timedelta(days=6)
    week_end = today
    gastos_semana = Expense.objects.filter(date__range=(week_start, week_end))
    gastos_semana_total = gastos_semana.aggregate(t=Sum('amount'))['t'] or 0
    gastos_semana_anterior_total = Expense.objects.filter(
        date__range=(week_start - timedelta(days=7), week_start - timedelta(days=1))
    ).aggregate(t=Sum('amount'))['t'] or 0

    gastos_mes = Expense.objects.filter(date__gte=month_start)
    gastos_mes_total = gastos_mes.aggregate(t=Sum('amount'))['t'] or 0
    gastos_total = Expense.objects.aggregate(t=Sum('amount'))['t'] or 0

    month_orders = Order.objects.filter(
        status=OrderStatus.COMPLETED,
        updated_at__date__gte=month_start,
        updated_at__date__lte=today,
    )
    ventas_mes = month_orders.aggregate(t=Sum('total'))['t'] or 0

    stock_bajo = Product.objects.filter(
        Q(stock__lt=10) | Q(stock=0)
    ).count()
    pedidos_pendientes = Order.objects.filter(
        status__in=[OrderStatus.PENDING, OrderStatus.READY]
    ).count()

    top = OrderItem.objects.values('product_name').annotate(
        total_qty=Sum('quantity'),
        total_ingreso=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField(max_digits=12, decimal_places=2)))
    ).order_by('-total_qty')[:5]

    top_with_images = []
    for p in top:
        product = Product.objects.filter(name=p['product_name']).first()
        top_with_images.append({
            'nombre': p['product_name'],
            'vendidos': p['total_qty'],
            'ingreso': float(p['total_ingreso']),
            'imagen': product.image.url if product and product.image else None,
        })

    total_productos = Product.objects.filter(is_available=True).count()

    return JsonResponse({
        'ventasHoy': float(ventas_hoy),
        'gastosHoy': float(gastos_hoy),
        'gananciaHoy': float(ventas_hoy - gastos_hoy),
        'ventasSemana': float(ventas_semana),
        'gastosSemana': float(gastos_semana_total),
        'gastosSemanaAnterior': float(gastos_semana_anterior_total),
        'gananciaSemana': float(ventas_semana - gastos_semana_total),
        'ventasMes': float(ventas_mes),
        'gastosMes': float(gastos_mes_total),
        'gananciaMes': float(ventas_mes - gastos_mes_total),
        'gastosTotal': float(gastos_total),
        'stockBajo': stock_bajo,
        'pedidosPendientes': pedidos_pendientes,
        'totalProductos': total_productos,
        'chartData': chart,
        'topProductos': top_with_images,
        'utilidadNeta': float(ventas_semana - gastos_mes_total),
        'weekStart': week_start_fmt,
        'weekEnd': week_end_fmt,
    })


@csrf_exempt
@require_http_methods(['GET'])
@_staff_required
def api_categorias(request):
    categorias = Category.objects.filter(is_active=True).order_by('name')
    data = [{'id': c.id, 'name': c.name} for c in categorias]
    return JsonResponse({'categorias': data})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@_staff_required
def api_productos(request):
    if request.method == 'GET':
        busqueda = request.GET.get('q', '')
        categoria = request.GET.get('categoria', '')
        productos = Product.objects.all()
        if busqueda:
            productos = productos.filter(
                Q(name__icontains=busqueda) | Q(slug__icontains=busqueda)
            )
        if categoria:
            productos = productos.filter(category__name=categoria)
        data = []
        for p in productos:
            batches = p.batches.all()
            total_stock = sum(b.quantity for b in batches) + p.stock
            codigo = _ensure_product_barcode(p)
            data.append({
                'id': p.id,
                'nombre': p.name,
                'codigo': codigo,
                'categoria': p.category.name if p.category else '',
                'precio': float(p.price),
                'precioCompra': float(p.cost_price),
                'stock': total_stock,
                'umbral': p.umbral,
                'color': '#d97706',
                'icono': 'fa-solid fa-box',
                'descripcion': p.description,
                'imagen': p.image.url if p.image else None,
                'lotes': [{
                    'id': b.id,
                    'numeroLote': b.batch_code,
                    'precio': float(b.cost_price),
                    'cantidad': b.quantity,
                    'fechaVencimiento': b.expiry_date.strftime('%d/%m/%Y') if b.expiry_date else '',
                    'proveedor': b.supplier,
                    'isLocked': b.is_locked,
                } for b in batches]
            })
        return JsonResponse({'productos': data})

    elif request.method == 'POST':
        categoria, _ = Category.objects.get_or_create(name=request.POST.get('categoria', 'General'))
        try:
            precio = Decimal(request.POST.get('precio', '0'))
        except (InvalidOperation, TypeError):
            precio = Decimal('0')
        try:
            precioCompra = Decimal(request.POST.get('precioCompra', '0'))
        except (InvalidOperation, TypeError):
            precioCompra = Decimal('0')
        try:
            stock = int(request.POST.get('stock', '0'))
        except (ValueError, TypeError):
            stock = 0
        try:
            umbral = int(request.POST.get('umbral', '10'))
        except (ValueError, TypeError):
            umbral = 10
        producto = Product.objects.create(
            category=categoria,
            name=request.POST.get('nombre', ''),
            description=request.POST.get('descripcion', ''),
            price=precio,
            cost_price=precioCompra,
            stock=stock,
            umbral=umbral,
        )
        codigo_recibido = request.POST.get('codigo', '').strip()
        if codigo_recibido and len(codigo_recibido) == 13 and codigo_recibido.isdigit():
            producto.codigo = codigo_recibido
            producto.save(update_fields=['codigo'])
        else:
            _ensure_product_barcode(producto)
        if 'imagen' in request.FILES:
            producto.image = request.FILES['imagen']
            producto.save()
        return JsonResponse({'success': True, 'id': producto.id})


@csrf_exempt
@require_http_methods(['GET', 'POST', 'PUT', 'DELETE'])
@_staff_required
def api_producto_detalle(request, producto_id):
    producto = get_object_or_404(Product, id=producto_id)
    if request.method == 'GET':
        return JsonResponse({
            'id': producto.id,
            'nombre': producto.name,
            'codigo': _ensure_product_barcode(producto),
            'descripcion': producto.description,
            'precio': float(producto.price),
            'stock': producto.stock,
        })
    elif request.method in ('PUT', 'POST'):
        if request.content_type and 'multipart/form-data' in request.content_type:
            producto.name = request.POST.get('nombre', producto.name)
            producto.description = request.POST.get('descripcion', producto.description)
            cat_name = request.POST.get('categoria', '')
            if cat_name:
                categoria, _ = Category.objects.get_or_create(name=cat_name)
                producto.category = categoria
            codigo_recibido = request.POST.get('codigo', '').strip()
            if codigo_recibido and len(codigo_recibido) == 13 and codigo_recibido.isdigit():
                producto.codigo = codigo_recibido
            else:
                _ensure_product_barcode(producto)
            try:
                producto.price = Decimal(request.POST.get('precio', str(producto.price)))
            except (InvalidOperation, TypeError):
                pass
            try:
                producto.cost_price = Decimal(request.POST.get('precioCompra', str(producto.cost_price)))
            except (InvalidOperation, TypeError):
                pass
            try:
                producto.stock = int(request.POST.get('stock', str(producto.stock)))
            except (ValueError, TypeError):
                pass
            try:
                producto.umbral = int(request.POST.get('umbral', str(producto.umbral)))
            except (ValueError, TypeError):
                pass
            if 'imagen' in request.FILES:
                producto.image = request.FILES['imagen']
        else:
            data = json.loads(request.body)
            producto.name = data.get('nombre', producto.name)
            producto.description = data.get('descripcion', producto.description)
            cat_name = data.get('categoria', '')
            if cat_name:
                categoria, _ = Category.objects.get_or_create(name=cat_name)
                producto.category = categoria
            try:
                producto.price = Decimal(str(data.get('precio', producto.price)))
            except (InvalidOperation, TypeError):
                pass
            try:
                producto.cost_price = Decimal(str(data.get('precioCompra', producto.cost_price)))
            except (InvalidOperation, TypeError):
                pass
            try:
                producto.umbral = int(data.get('umbral', producto.umbral))
            except (ValueError, TypeError):
                pass
            producto.stock = data.get('stock', producto.stock)
        producto.save()
        return JsonResponse({'success': True})
    elif request.method == 'DELETE':
        producto.delete()
        return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@_staff_required
def api_lotes(request, producto_id):
    producto = get_object_or_404(Product, id=producto_id)
    if request.method == 'GET':
        lotes = producto.batches.all()
        data = [{
            'id': b.id,
            'numeroLote': b.batch_code,
            'precio': float(b.cost_price),
            'cantidad': b.quantity,
            'fechaVencimiento': b.expiry_date.strftime('%d/%m/%Y') if b.expiry_date else '',
            'proveedor': b.supplier,
            'isLocked': b.is_locked,
        } for b in lotes]
        return JsonResponse({'lotes': data})
    elif request.method == 'POST':
        body = json.loads(request.body)
        try:
            cost_price = Decimal(str(body.get('precio', 0)))
        except (InvalidOperation, TypeError):
            cost_price = Decimal('0')
        try:
            quantity = int(body.get('cantidad', 0))
        except (ValueError, TypeError):
            quantity = 0
        lote = ProductBatch.objects.create(
            product=producto,
            cost_price=cost_price,
            quantity=quantity,
            expiry_date=body.get('fechaVencimiento', None) or None,
            supplier=body.get('proveedor', ''),
        )
        producto.cost_price = cost_price
        producto.save()
        return JsonResponse({'success': True, 'id': lote.id, 'batch_code': lote.batch_code})


@csrf_exempt
@require_http_methods(['GET', 'PUT'])
@_staff_required
def api_lote_detalle(request, producto_id, lote_id):
    producto = get_object_or_404(Product, id=producto_id)
    lote = get_object_or_404(ProductBatch, id=lote_id, product=producto)
    if request.method == 'GET':
        return JsonResponse({
            'lote': {
                'id': lote.id,
                'numeroLote': lote.batch_code,
                'precio': float(lote.cost_price),
                'cantidad': lote.quantity,
                'fechaVencimiento': lote.expiry_date.strftime('%Y-%m-%d') if lote.expiry_date else '',
                'proveedor': lote.supplier,
                'isLocked': lote.is_locked,
            }
        })

    if lote.is_locked:
        return JsonResponse({'success': False, 'error': 'Este lote no puede ser editado porque ya fue modificado por una venta.'}, status=400)

    body = json.loads(request.body)

    if lote.is_locked:
        lote.expiry_date = body.get('fechaVencimiento', None) or None
        lote.supplier = body.get('proveedor', lote.supplier)
        lote.save()
        return JsonResponse({'success': True})

    try:
        cost_price = Decimal(str(body.get('precio', lote.cost_price)))
    except (InvalidOperation, TypeError):
        cost_price = lote.cost_price
    try:
        quantity = int(body.get('cantidad', lote.quantity))
    except (ValueError, TypeError):
        quantity = lote.quantity

    lote.cost_price = cost_price
    lote.quantity = quantity
    lote.expiry_date = body.get('fechaVencimiento', None) or None
    lote.supplier = body.get('proveedor', lote.supplier)
    lote.save()

    producto.cost_price = cost_price
    producto.save(update_fields=['cost_price'])
    return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(['GET'])
@_staff_required
def api_pedidos(request):
    orders = Order.objects.select_related('user', 'completed_by').filter(
        boleta_code__isnull=False,
        is_paid=True,
        status__in=[OrderStatus.PENDING, OrderStatus.READY]
    ).order_by('-created_at')
    data = [{
        'id': o.id,
        'cliente': o.user.get_full_name() or o.user.username,
        'items': o.items.count(),
        'total': float(o.total),
        'estado': o.get_status_display(),
        'estado_key': o.status,
        'canal': 'Online',
        'fecha': o.created_at.strftime('%d/%m/%Y %H:%M'),
        'direccion': o.user.profile.address if hasattr(o.user, 'profile') else '',
        'metodo_pago': o.get_payment_method_display() if o.payment_method else '',
        'metodo_key': o.payment_method or '',
        'transfer_bank': o.transfer_bank or '',
        'boleta_code': o.boleta_code or '',
        'is_paid': o.is_paid,
        'validated_by': o.completed_by.get_full_name() or o.completed_by.username if o.completed_by else None,
    } for o in orders]
    return JsonResponse({'pedidos': data})


@csrf_exempt
@require_http_methods(['PUT'])
@_staff_required
def api_pedido_estado(request, pedido_id):
    pedido = get_object_or_404(Order, id=pedido_id)
    body = json.loads(request.body)
    nuevo_estado = body.get('estado', '')
    estado_map = {
        'Pendiente': OrderStatus.PENDING,
        'Listo para entrega': OrderStatus.READY,
        'Listo': OrderStatus.READY,
        'Completado': OrderStatus.COMPLETED,
        'Cancelado': OrderStatus.CANCELLED,
    }
    if nuevo_estado in estado_map:
        mapped = estado_map[nuevo_estado]
        if mapped == OrderStatus.COMPLETED:
            pedido.completed_at = timezone.now()
            pedido.completed_by = request.user
        elif mapped == OrderStatus.READY:
            pedido.ready_at = timezone.now()
            pedido.ready_by = request.user
        pedido.status = mapped
        pedido.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Estado inválido'}, status=400)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@_staff_required
def api_ventas(request):
    if request.method == 'GET':
        orders = Order.objects.select_related('user', 'created_by', 'completed_by').filter(
            status__in=[OrderStatus.COMPLETED, OrderStatus.READY, OrderStatus.CANCELLED]
        ).order_by('-created_at')
        data = []
        trabajadores_set = set()
        for o in orders:
            if o.created_by:
                canal = 'Presencial'
                cliente = o.customer_name if o.customer_name else '-'
                trabajador = o.created_by.get_full_name() or o.created_by.username
            else:
                canal = 'Online'
                cliente = o.customer_name if o.customer_name else (o.user.get_full_name() or o.user.username)
                trabajador = o.completed_by.get_full_name() or o.completed_by.username if o.completed_by else ''
            if trabajador:
                trabajadores_set.add(trabajador)
            data.append({
                'id': o.id,
                'boleta_code': o.boleta_code or '',
                'cliente': cliente,
                'trabajador': trabajador,
                'canal': canal,
                'total': float(o.total),
                'metodo': o.get_payment_method_display() if o.payment_method else 'Efectivo',
                'metodo_key': o.payment_method or 'cash',
                'transfer_bank': o.transfer_bank or '',
                'estado': 'Cancelada' if o.status == OrderStatus.CANCELLED else ('Completada' if o.is_paid else 'Pendiente'),
                'fecha': o.created_at.strftime('%d/%m/%Y'),
                'items': o.items.count(),
            })
        return JsonResponse({'ventas': data, 'trabajadores': sorted(trabajadores_set)})

    elif request.method == 'POST':
        from django.db import transaction

        body = json.loads(request.body)
        items = body.get('items', [])
        metodo = body.get('metodo', 'Efectivo')

        is_digital = metodo in ('Yape', 'Plin', 'Transferencia')
        metodo_map = {
            'Efectivo': 'cash',
            'Yape': 'yape',
            'Plin': 'plin',
            'Transferencia': 'transfer',
        }
        payment_method = metodo_map.get(metodo, 'cash')

        with transaction.atomic():
            total = 0
            order = Order.objects.create(
                user=request.user,
                created_by=request.user,
                customer_name='-',
                status=OrderStatus.PENDING if is_digital else OrderStatus.COMPLETED,
                payment_method=payment_method,
                total=0,
                is_paid=False if is_digital else True,
            )

            if not is_digital:
                order.paid_at = timezone.now()
                order.completed_at = timezone.now()

            order.boleta_code = generate_boleta_code()

            for item in items:
                product = Product.objects.filter(id=item.get('id')).first()
                quantity = int(item['cantidad'])
                price = float(item['precio'])
                total += price * quantity

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=item['nombre'],
                    quantity=quantity,
                    price=price,
                )

                if product:
                    _reduce_stock_fifo(product, quantity)

            order.total = total
            order.save()

        response_data = {'success': True, 'id': order.id, 'boleta_code': order.boleta_code}

        if is_digital:
            view_name_map = {
                'Yape': 'payment_simulation:yape_with_order',
                'Plin': 'payment_simulation:plin_with_order',
                'Transferencia': 'payment_simulation:bcp_transfer_with_order',
            }
            sim_view_name = view_name_map.get(metodo, 'payment_simulation:home')
            sim_absolute_url = build_simulation_absolute_uri(
                request, sim_view_name, **{'order_id': order.id}
            )
            sim_qr_b64 = _generate_qr_base64(sim_absolute_url)
            sim_url = reverse(sim_view_name, kwargs={'order_id': order.id})

            response_data.update({
                'pending_payment': True,
                'simulation_url': sim_url,
                'simulation_qr_b64': sim_qr_b64,
            })

        return JsonResponse(response_data)


@csrf_exempt
@require_http_methods(['POST'])
@_staff_required
def api_venta_completar_pago(request, venta_id):
    order = get_object_or_404(Order, id=venta_id)
    order.is_paid = True
    order.paid_at = timezone.now()
    order.completed_at = timezone.now()
    order.completed_by = request.user
    order.status = OrderStatus.COMPLETED
    order.save()
    return JsonResponse({'success': True})


def _parse_request_body(request):
    if request.content_type and 'multipart' in request.content_type:
        return request.POST.dict(), request.FILES
    try:
        body = json.loads(request.body) if request.body else {}
    except (json.JSONDecodeError, AttributeError):
        body = request.POST.dict()
    return body, request.FILES


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@_staff_required
def api_gastos(request):
    if request.method == 'GET':
        gastos = Expense.objects.all().order_by('-created_at')
        data = [{
            'id': g.id,
            'concepto': g.concept,
            'tipo': g.type,
            'monto': float(g.amount),
            'fecha': g.date.strftime('%d/%m/%Y'),
            'descripcion': g.description,
            'comprobante_url': get_signed_url(g.comprobante),
            'comprobante_nombre': g.comprobante.name.split('/')[-1] if g.comprobante else None,
        } for g in gastos]
        return JsonResponse({'gastos': data})

    elif request.method == 'POST':
        body, files = _parse_request_body(request)
        gasto = Expense.objects.create(
            concept=body['concepto'],
            type=body['tipo'],
            amount=body['monto'],
            date=body['fecha'],
            description=body.get('descripcion', ''),
            created_by=request.user,
            comprobante=files.get('comprobante'),
        )
        return JsonResponse({
            'success': True,
            'id': gasto.id,
            'comprobante_url': get_signed_url(gasto.comprobante),
        })


@csrf_exempt
@require_http_methods(['GET', 'POST', 'DELETE'])
@_staff_required
def api_gasto_detalle(request, gasto_id):
    gasto = get_object_or_404(Expense, id=gasto_id)
    if request.method == 'GET':
        return JsonResponse({
            'id': gasto.id,
            'concepto': gasto.concept,
            'tipo': gasto.type,
            'monto': float(gasto.amount),
            'fecha': gasto.date.strftime('%d/%m/%Y'),
            'descripcion': gasto.description,
            'comprobante_url': get_signed_url(gasto.comprobante),
            'comprobante_nombre': gasto.comprobante.name.split('/')[-1] if gasto.comprobante else None,
        })
    elif request.method == 'POST':
        body, files = _parse_request_body(request)
        gasto.concept = body.get('concepto', gasto.concept)
        gasto.type = body.get('tipo', gasto.type)
        gasto.amount = body.get('monto', gasto.amount)
        gasto.date = body.get('fecha', gasto.date)
        gasto.description = body.get('descripcion', gasto.description)
        if 'comprobante' in files:
            gasto.comprobante = files['comprobante']
        elif body.get('comprobante_clear'):
            gasto.comprobante.delete()
            gasto.comprobante = None
        gasto.save()
        return JsonResponse({'success': True, 'comprobante_url': get_signed_url(gasto.comprobante)})
    elif request.method == 'DELETE':
        gasto.delete()
        return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@_staff_required
def api_usuarios(request):
    if request.method == 'GET':
        usuarios = User.objects.select_related('profile').all()
        data = [{
            'id': u.id,
            'nombre': u.first_name or u.username,
            'apellido': u.last_name or '',
            'email': u.email,
            'rol': u.profile.role.name if u.profile.role else 'client',
            'activo': u.is_active,
            'username': u.username,
            'telefono': u.profile.phone if hasattr(u, 'profile') else '',
            'fechaRegistro': u.date_joined.strftime('%d/%m/%Y'),
        } for u in usuarios]
        return JsonResponse({'usuarios': data})

    elif request.method == 'POST':
        body = json.loads(request.body)
        nombre = body.get('nombre', '').strip()
        apellido = body.get('apellido', '').strip()
        email = body.get('email', '').strip()
        telefono = body.get('telefono', '')
        rol = body.get('rol', 'employee')
        username = body.get('username', '').strip()

        if not nombre or not email or not username:
            return JsonResponse({'success': False, 'error': 'Nombre, email y nombre de usuario son obligatorios'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un usuario con ese email'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'El nombre de usuario ya está en uso'}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=nombre,
            last_name=apellido,
            password='Cambiar123++',
        )

        if rol in ('admin', 'employee'):
            user.is_staff = True
            user.save()

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = Role.objects.get(name=rol)
        profile.phone = telefono
        profile.must_change_password = True
        profile.save()

        return JsonResponse({'success': True, 'id': user.id, 'username': username})


@csrf_exempt
@require_http_methods(['GET', 'PUT'])
@_staff_required
def api_usuario_detalle(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'GET':
        return JsonResponse({
            'id': usuario.id,
            'nombre': usuario.first_name or usuario.username,
            'apellido': usuario.last_name or '',
            'email': usuario.email,
            'rol': usuario.profile.role.name if hasattr(usuario, 'profile') and usuario.profile.role else 'client',
            'activo': usuario.is_active,
            'username': usuario.username,
            'telefono': usuario.profile.phone if hasattr(usuario, 'profile') else '',
            'fechaRegistro': usuario.date_joined.strftime('%d/%m/%Y'),
        })
    elif request.method == 'PUT':
        body = json.loads(request.body)
        nombre = body.get('nombre', '').strip()
        apellido = body.get('apellido', '').strip()
        email = body.get('email', '').strip()
        telefono = body.get('telefono', '')
        rol = body.get('rol', '')
        username = body.get('username', '').strip()

        if email and email != usuario.email:
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'Ya existe un usuario con ese email'}, status=400)
            usuario.email = email

        if username and username != usuario.username:
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'El nombre de usuario ya está en uso'}, status=400)
            usuario.username = username

        if nombre:
            usuario.first_name = nombre
        if apellido:
            usuario.last_name = apellido
        usuario.save()

        if hasattr(usuario, 'profile'):
            if rol:
                usuario.profile.role = Role.objects.get(name=rol)
            usuario.profile.phone = telefono
            usuario.profile.save()

        return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(['POST'])
@_staff_required
def api_usuario_toggle(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    usuario.is_active = not usuario.is_active
    usuario.save()
    return JsonResponse({'success': True, 'activo': usuario.is_active})


@csrf_exempt
@require_http_methods(['POST'])
@_staff_required
def api_usuario_reset_password(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    usuario.set_password('Cambiar123++')
    usuario.save()
    profile, _ = UserProfile.objects.get_or_create(user=usuario)
    profile.must_change_password = True
    profile.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(['GET'])
@_staff_required
def api_pedido_detalle_admin(request, pedido_id):
    order = get_object_or_404(
        Order.objects.select_related('user', 'ready_by', 'completed_by'),
        id=pedido_id
    )
    items = []
    for item in order.items.all():
        items.append({
            'name': item.product_name,
            'quantity': item.quantity,
            'price': float(item.price),
            'subtotal': float(item.subtotal),
            'image': item.product.image.url if item.product and item.product.image else None,
        })
    from apps.orders.services.qr_service import generate_qr_base64
    from django.urls import reverse
    from payment_simulation.utils import build_simulation_absolute_uri
    boleta_url = build_simulation_absolute_uri(
        request, 'validar_boleta', boleta_code=order.boleta_code
    ) if order.boleta_code else ''
    qr_b64 = generate_qr_base64(boleta_url) if boleta_url else ''
    data = {
        'id': order.pk,
        'boleta_code': order.boleta_code or '',
        'cliente': order.user.get_full_name() or order.user.username,
        'cliente_email': order.user.email,
        'fecha': order.created_at.strftime('%d/%m/%Y %H:%M'),
        'direccion': order.user.profile.address if hasattr(order.user, 'profile') else '',
        'metodo_pago': order.get_payment_method_display() if order.payment_method else '',
        'estado': order.get_status_display(),
        'estado_key': order.status,
        'total': float(order.total),
        'notes': order.notes or '',
        'is_paid': order.is_paid,
        'items': items,
        'qr_b64': qr_b64,
        'ready_at': order.ready_at.strftime('%d/%m/%Y %H:%M') if order.ready_at else None,
        'completed_at': order.completed_at.strftime('%d/%m/%Y %H:%M') if order.completed_at else None,
        'ready_by': order.ready_by.get_full_name() or order.ready_by.username if order.ready_by else None,
        'completed_by': order.completed_by.get_full_name() or order.completed_by.username if order.completed_by else None,
    }
    return JsonResponse({'success': True, 'order': data})


@csrf_exempt
@require_http_methods(['POST'])
@_staff_required
def api_pedido_marcar_listo(request, pedido_id):
    order = get_object_or_404(Order, id=pedido_id)
    result = OrderService.mark_as_ready(order, request.user)
    if result['success']:
        create_notification(
            user=order.user,
            title="Pedido listo para entrega",
            message=f"Tu pedido N°{order.order_number or str(order.pk).zfill(6)} ya está listo. Puedes acercarte a recogerlo.",
            notification_type="order_ready",
        )
        try:
            send_order_ready_email(order)
        except Exception:
            pass
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(['POST'])
@_staff_required
def api_pedido_completar_qr(request, pedido_id):
    order = get_object_or_404(Order, id=pedido_id)
    result = OrderService.mark_as_completed(order, request.user)
    if result['success']:
        create_notification(
            user=order.user,
            title="Pedido completado",
            message=f"Tu pedido N°{order.order_number or str(order.pk).zfill(6)} ha sido entregado con éxito. ¡Gracias por tu compra!",
            notification_type="order_completed",
        )
        try:
            from apps.orders.services.email_service import send_order_delivered_email
            send_order_delivered_email(order)
        except Exception:
            pass
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(['GET'])
def api_notificaciones(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=403)
    notifs = Notification.objects.filter(user=request.user)[:50]
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
        'notification_type': n.notification_type,
    } for n in notifs]
    return JsonResponse({'success': True, 'notifications': data})


@csrf_exempt
@require_http_methods(['GET'])
def api_notificaciones_contador(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'count': 0}, status=403)
    count = get_unread_count(request.user)
    return JsonResponse({'success': True, 'count': count})


@csrf_exempt
@require_http_methods(['POST'])
def api_notificaciones_leer(request, notif_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False}, status=403)
    mark_as_read(notif_id, request.user)
    return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(['POST'])
def api_notificaciones_leer_todas(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False}, status=403)
    mark_all_as_read(request.user)
    return JsonResponse({'success': True})


@login_required
def notificaciones_view(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:100]
    unread_count = get_unread_count(request.user)
    return render(request, 'core/notificaciones.html', {
        'notifications': notifs,
        'unread_count': unread_count,
    })


@csrf_exempt
@require_http_methods(['POST'])
def api_qr_scan(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Debes iniciar sesión para validar una boleta'}, status=401)
    if not (request.user.is_staff or
            (hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.name in ('admin', 'employee'))):
        return JsonResponse({'success': False, 'error': 'No tienes permisos para validar boletas'}, status=403)

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    boleta_code = body.get('boleta_code', '').strip()
    if not boleta_code:
        return JsonResponse({'success': False, 'error': 'Código de boleta requerido'}, status=400)

    try:
        order = Order.objects.get(boleta_code=boleta_code)
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Boleta no encontrada'}, status=404)

    if order.status != OrderStatus.READY:
        return JsonResponse({
            'success': False,
            'error': f'El pedido no está listo para entrega. Estado actual: {order.get_status_display()}'
        }, status=400)

    result = OrderService.mark_as_completed(order, request.user)
    if result['success']:
        create_notification(
            user=order.user,
            title="Pedido completado",
            message=f"Tu pedido N°{order.order_number or str(order.pk).zfill(6)} ha sido entregado con éxito. ¡Gracias por tu compra!",
            notification_type="order_completed",
        )
        try:
            from apps.orders.services.email_service import send_order_delivered_email
            send_order_delivered_email(order)
        except Exception:
            pass
    return JsonResponse(result)


@_staff_required
def validar_boleta_view(request, boleta_code):
    order = get_object_or_404(Order, boleta_code=boleta_code)
    context = {
        'boleta_code': boleta_code,
        'order_id': order.pk,
        'order_number': order.order_number or str(order.pk).zfill(6),
        'order_status': order.status,
        'order_status_display': order.get_status_display(),
        'cliente': order.user.get_full_name() or order.user.username,
        'total': float(order.total),
        'validated_by': order.completed_by.get_full_name() or order.completed_by.username if order.completed_by else None,
    }
    return render(request, 'core/validar_boleta.html', context)
