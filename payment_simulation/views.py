from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone
import random
from apps.orders.models import Notification, Order, OrderStatus, Cart
from apps.orders.services.order_service import generate_order_number


def _mark_order_paid(order):
    order.is_paid = True
    order.paid_at = timezone.now()
    order.status = OrderStatus.PENDING
    if not order.order_number:
        order.order_number = generate_order_number()
    order.save()
    Cart.objects.filter(user=order.user).delete()
    Notification.objects.create(
        user=order.user,
        title="Pago confirmado",
        message=f"Tu pago del pedido N°{order.order_number} ha sido confirmado. Pronto lo estaremos preparando.",
        notification_type="payment_confirmed",
    )
    try:
        from apps.orders.services.email_service import send_receipt_email
        send_receipt_email(order)
    except Exception:
        pass


def simulation_home(request):
    pending_orders = Order.objects.filter(status='pending').order_by('-created_at')[:10]
    return render(request, 'payment_simulation/home.html', {
        'pending_orders': pending_orders
    })


def yape_home(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'pay':
            _mark_order_paid(order)
            return render(request, 'payment_simulation/yape_home.html', {
                'order': order,
                'success': True,
            })
        elif action == 'show_orders':
            return redirect('payment_simulation:yape_pedidos')
    return render(request, 'payment_simulation/yape_home.html', {'order': order})


def yape_qr(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'pay':
            _mark_order_paid(order)
            return render(request, 'payment_simulation/yape_qr.html', {
                'order': order,
                'success': True,
            })
    return render(request, 'payment_simulation/yape_qr.html', {'order': order})


def yape_code(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'validate_code':
            entered_code = request.POST.get('code', '')
            if order.generated_yape_code == entered_code:
                _mark_order_paid(order)
                return render(request, 'payment_simulation/yape_code.html', {
                    'order': order,
                    'success': True,
                })
            else:
                code = str(random.randint(100000, 999999))
                order.generated_yape_code = code
                order.save()
                return render(request, 'payment_simulation/yape_code.html', {
                    'order': order,
                    'yape_code': code,
                    'code_error': True,
                })

    code = str(random.randint(100000, 999999))
    order.generated_yape_code = code
    order.save()
    return render(request, 'payment_simulation/yape_code.html', {
        'order': order,
        'yape_code': code,
    })


def yape_entry(request):
    return render(request, 'payment_simulation/yape_entry.html')


def yape_pedidos(request):
    pending_orders = Order.objects.filter(status='pending').order_by('-created_at')[:10]
    from_param = request.GET.get('from', '')
    return render(request, 'payment_simulation/yape_pedidos.html', {
        'pending_orders': pending_orders,
        'from_param': from_param,
    })


def plin_entry(request):
    return render(request, 'payment_simulation/plin_entry.html')


def plin_home(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'pay':
            _mark_order_paid(order)
            return render(request, 'payment_simulation/plin_home.html', {
                'order': order,
                'success': True,
            })
        elif action == 'show_orders':
            return redirect('payment_simulation:plin_pedidos')
    return render(request, 'payment_simulation/plin_home.html', {'order': order})


def plin_qr(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'pay':
            _mark_order_paid(order)
            return render(request, 'payment_simulation/plin_qr.html', {
                'order': order,
                'success': True,
            })
    return render(request, 'payment_simulation/plin_qr.html', {'order': order})


def plin_pedidos(request):
    pending_orders = Order.objects.filter(status='pending').order_by('-created_at')[:10]
    from_param = request.GET.get('from', '')
    return render(request, 'payment_simulation/plin_pedidos.html', {
        'pending_orders': pending_orders,
        'from_param': from_param,
    })


def bcp_transfer_simulation(request, order_id=None):
    if request.method == 'POST':
        raw_id = request.POST.get('order_id', '')

        if not raw_id or not raw_id.isdigit():
            return redirect('payment_simulation:home')

        order = get_object_or_404(Order, id=int(raw_id))
        _mark_order_paid(order)
        order.payment_method = 'transferencia_bcp'
        order.transfer_bank = 'bcp'
        order.save(update_fields=['payment_method', 'transfer_bank'])
        return render(request, 'payment_simulation/bcp_transfer.html', {
            'order': order,
            'success': True
        })

    if order_id:
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'payment_simulation/bcp_transfer.html', {'order': order})

    pending_orders = Order.objects.filter(status='pending').order_by('-created_at')[:10]
    return render(request, 'payment_simulation/bcp_transfer.html', {'pending_orders': pending_orders})


def interbank_transfer_simulation(request, order_id=None):
    if request.method == 'POST':
        raw_id = request.POST.get('order_id', '')

        if not raw_id or not raw_id.isdigit():
            return redirect('payment_simulation:home')

        order = get_object_or_404(Order, id=int(raw_id))
        _mark_order_paid(order)
        order.payment_method = 'transferencia_interbank'
        order.transfer_bank = 'interbank'
        order.save(update_fields=['payment_method', 'transfer_bank'])
        return render(request, 'payment_simulation/interbank_transfer.html', {
            'order': order,
            'success': True
        })

    if order_id:
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'payment_simulation/interbank_transfer.html', {'order': order})

    pending_orders = Order.objects.filter(status='pending').order_by('-created_at')[:10]
    return render(request, 'payment_simulation/interbank_transfer.html', {'pending_orders': pending_orders})


def check_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return JsonResponse({
        'is_paid': order.is_paid,
        'status': order.status,
        'boleta_code': order.boleta_code
    })


def validate_yape_code(request, order_id, code):
    order = get_object_or_404(Order, id=order_id)
    if order.generated_yape_code == code:
        _mark_order_paid(order)
        return JsonResponse({'success': True, 'boleta_code': order.boleta_code})
    return JsonResponse({'success': False})


def validate_plin_code(request, order_id, code):
    order = get_object_or_404(Order, id=order_id)
    if order.generated_yape_code == code:
        _mark_order_paid(order)
        return JsonResponse({'success': True, 'boleta_code': order.boleta_code})
    return JsonResponse({'success': False})
