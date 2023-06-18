from django.shortcuts import redirect, render, get_object_or_404
from services.models import Service 
from .models import Cart, CartItem 
from order.models import Order, OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import stripe 

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart 

def add_cart(request, service_id):
    service = Service.objects.get(id=service_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id = _cart_id(request))
        cart.save() 
    try:
        cart_item = CartItem.objects.get(service=service, cart=cart)
        if cart_item.quantity < cart_item.service.job_limit:
            cart_item.quantity += 1 
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(service=service, quantity = 1, cart=cart)
        cart_item.save()
    return redirect('cart:cart_detail')

def cart_detail(request, total=0, counter=0, cart_items = None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.service.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    stripe.api_key = settings.STRIPE_SECRET_KEY 
    stripe_total = int(total*100)
    description = 'Tenner | Order'
    data_key = settings.STRIPE_PUBLISHABLE_KEY 
    if request.method=='POST':
        print(request.POST)
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            billingName = request.POST['stripeBillingName']
            billingAddress1 = request.POST['stripeBillingAddressLine1']
            billingcity = request.POST['stripeBillingAddressCity']
            billingCountry = request.POST['stripeBillingAddressCountryCode']

            customer = stripe.Customer.create(email=email, source=token)
            stripe.Charge.create(amount=stripe_total,
            currency="eur",
            description=description,
            customer=customer.id)
            try:
                order_details = Order.objects.create(
                    token = token,
                    total = total,
                    emailAddress = email,
                    billingName = billingName,
                    billingAddress1 = billingAddress1,
                    billingCity = billingcity,
                    billingCountry = billingCountry,
                )
                order_details.save()
                for order_item in cart_items:
                    oi = OrderItem.objects.create(
                        service = order_item.service.name,
                        quantity = order_item.quantity,
                        price = order_item.service.price,
                        order = order_details)
                    oi.save
                    services = Service.objects.get(id=order_item.service.id)
                    services.job_limit = int(order_item.service.job_limit - order_item.quantity)
                    services.save()
                    order_item.delete()
                    print('The order has been created')
                return redirect ('order:thanks', order_details.id)
            except ObjectDoesNotExist:
                pass

        except stripe.error.CardError as e:
            return e
    return render(request, 'cart.html', {'cart_items':cart_items, 'total':total, 'counter':counter,
    'data_key':data_key, 'stripe_total':stripe_total,
    'description':description})

def full_remove(request, service_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    service = get_object_or_404(Service, id=service_id)
    cart_item = CartItem.objects.get(service=service, cart=cart)
    cart_item.delete()
    return redirect('cart:cart_detail')

