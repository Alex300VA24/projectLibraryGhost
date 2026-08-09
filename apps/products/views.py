import json
from decimal import Decimal, InvalidOperation

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.decorators import staff_required
from .models import Category, Product, ProductBatch, ScanQueue
from .serializers import ProductSerializer, ScanQueueSerializer


def catalog_view(request):
    category_slug = request.GET.get('category')
    search = request.GET.get('q', '') or request.GET.get('search', '')
    page = request.GET.get('page', 1)

    products = Product.objects.filter(is_available=True)
    categories = Category.objects.filter(is_active=True)

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )

    paginator = Paginator(products, 16)
    try:
        products_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        products_page = paginator.page(1)

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)

    return render(request, 'products/catalog.html', {
        'products': products_page.object_list,
        'categories': categories,
        'selected_category': selected_category,
        'search': search,
        'page': products_page.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
    })


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(pk=product.pk)[:4]

    total_stock = sum(b.quantity for b in product.batches.all()) + product.stock

    return render(request, 'products/product_detail.html', {
        'product': product,
        'total_stock': total_stock,
        'related_products': related_products,
    })


def catalog_api_data(request):
    category_slug = request.GET.get('category')
    search = request.GET.get('q', '') or request.GET.get('search', '')
    page = request.GET.get('page', 1)

    products = Product.objects.filter(is_available=True)
    categories = Category.objects.filter(is_active=True)

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )

    paginator = Paginator(products, 16)
    try:
        products_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        products_page = paginator.page(1)

    products_data = [{
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'price': float(p.price),
        'stock': sum(b.quantity for b in p.batches.all()) + p.stock,
        'category': p.category.name,
        'description': p.description or '',
        'image': p.image.url if p.image else None,
    } for p in products_page]

    categories_data = [{
        'name': c.name,
        'slug': c.slug,
    } for c in categories]

    pagination = {
        'current_page': products_page.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'has_previous': products_page.has_previous(),
        'has_next': products_page.has_next(),
    }

    return JsonResponse({
        'success': True,
        'products': products_data,
        'categories': categories_data,
        'pagination': pagination,
    })


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@staff_required
def api_productos(request):
    if request.method == 'GET':
        busqueda = request.GET.get('q', '')
        categoria = request.GET.get('categoria', '')
        productos = Product.objects.all()
        if busqueda:
            productos = productos.filter(
                Q(name__icontains=busqueda) | Q(slug__icontains=busqueda) | Q(codigo__icontains=busqueda)
            )
        if categoria:
            productos = productos.filter(category__name=categoria)
        data = []
        for p in productos:
            batches = p.batches.all()
            total_stock = sum(b.quantity for b in batches) + p.stock
            data.append({
                'id': p.id,
                'nombre': p.name,
                'codigo': p.codigo or p.slug,
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
        if 'imagen' in request.FILES:
            producto.image = request.FILES['imagen']
            producto.save()
        return JsonResponse({'success': True, 'id': producto.id})


@csrf_exempt
@require_http_methods(['GET', 'POST', 'DELETE'])
@staff_required
def api_producto_detalle(request, producto_id=None):
    if request.method == 'GET':
        producto = get_object_or_404(Product, id=producto_id)
        total_stock = sum(b.quantity for b in producto.batches.all()) + producto.stock
        return JsonResponse({
            'id': producto.id,
            'nombre': producto.name,
            'descripcion': producto.description,
            'precio': float(producto.price),
            'stock': total_stock,
        })

    elif request.method == 'POST':
        if producto_id:  # si viene id, actualiza
            producto = get_object_or_404(Product, id=producto_id)
        else:  # si no, crea nuevo
            producto = Product()

        if request.content_type and 'multipart/form-data' in request.content_type:
            producto.name = request.POST.get('nombre', producto.name)
            producto.description = request.POST.get('descripcion', producto.description)
            cat_name = request.POST.get('categoria', '')
            if cat_name:
                categoria, _ = Category.objects.get_or_create(name=cat_name)
                producto.category = categoria
            try:
                producto.price = Decimal(request.POST.get('precio', str(producto.price)))
            except (InvalidOperation, TypeError):
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

        producto.save()
        return JsonResponse({'success': True})

    elif request.method == 'DELETE':
        producto = get_object_or_404(Product, id=producto_id)
        producto.delete()
        return JsonResponse({'success': True})




@csrf_exempt
@require_http_methods(['GET', 'POST'])
@staff_required
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
            batch_code=body.get('numeroLote', 'LOT-' + str(producto.batches.count() + 1)),
            cost_price=cost_price,
            quantity=quantity,
            expiry_date=body.get('fechaVencimiento', None) or None,
            supplier=body.get('proveedor', ''),
        )
        producto.cost_price = cost_price
        producto.save()
        return JsonResponse({'success': True, 'id': lote.id})


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def scanner_barcode(request):
    barcode = request.data.get('barcode', '').strip()
    if not barcode:
        return Response({'error': "El campo 'barcode' es requerido."},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        producto = Product.objects.get(codigo__exact=barcode)
        serializer = ProductSerializer(producto)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'error': 'Error interno del servidor'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def product_by_barcode(request, barcode):
    barcode = barcode.strip()
    try:
        producto = Product.objects.get(codigo__exact=barcode)
        serializer = ProductSerializer(producto)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'error': 'Error interno del servidor'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def scan_queue_add(request):
    barcode = request.data.get('barcode', '').strip()
    if not barcode:
        return Response({'error': "El campo 'barcode' es requerido."},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        producto = Product.objects.get(codigo__exact=barcode)
        queue_item = ScanQueue.objects.create(
            product=producto,
            barcode=barcode,
            status='pending'
        )
        serializer = ScanQueueSerializer(queue_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'error': 'Error interno del servidor'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def scan_queue_pending(request):
    items = ScanQueue.objects.filter(status='pending').select_related('product')
    serializer = ScanQueueSerializer(items, many=True)
    return Response({'items': serializer.data})


@api_view(['POST'])
def scan_queue_consume(request):
    ids = request.data.get('ids', [])
    if not ids:
        return Response({'error': 'Lista de ids requerida.'},
                        status=status.HTTP_400_BAD_REQUEST)
    updated = ScanQueue.objects.filter(id__in=ids, status='pending').update(status='consumed')
    return Response({'success': True, 'consumed': updated})
