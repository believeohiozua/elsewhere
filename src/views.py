from django.conf import settings   
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import FormTypeForm, CheckoutForm, CouponForm, RefundForm, PaymentForm, MyCustomSignupForm
#my Views
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, Profile


def is_valid_form(values): 
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class Profile(DetailView):
    model = Profile   
    template_name = "main/userprofile.html"


class IndexView(ListView):
    model = Item
    paginate_by = 10
    template_name = "main/index.html"
############################################################################################
class CheckoutView(View):
    
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = CheckoutForm()
        couponform= CouponForm()
        context={
                'form': form,
                'order': order,
                'DISPLAY_COUPON_FORM': True,
                'couponform': couponform,
                    }
        return render(self.request, 'main/checkout.html', context)

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            couponform= CouponForm()
            context = {
                'form': form,
                'order': order,
                'DISPLAY_COUPON_FORM': True,
                'couponform': couponform,
            }
            shipping_adress_qs = Address.objects.filter(
                user=self.request.user,               
                default=True
            )
            if shipping_adress_qs.exists():
                context.update(
                    {'default_shipping_street': shipping_adress_qs[0]})            
            return render(self.request, "main/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("src:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("\nUsing the defualt shipping address\n")
                    address_qs = Address.objects.filter(
                        user=self.request.user,                       
                        default=True
                    )
                   
                    if address_qs.exists():
                        shipping_location = address_qs[0].shipping_state
                        if shipping_location == 'Edo':
                            shipping_fee = 500
                        else:
                            shipping_fee = 1500
                        order.shipping_fee=shipping_fee
                        order.shipping_fee.save()

                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('src:checkout')
                else:
                    print("\nUser is entering a new shipping address\n")
                    shipping_street = form.cleaned_data.get(
                        'shipping_street')                    
                    shipping_state = form.cleaned_data.get(
                        'shipping_state')
                    shipping_lga=form.cleaned_data.get('shipping_lga')
                    phone_number=form.cleaned_data.get('phone_number')

                    if is_valid_form([shipping_street, shipping_state, shipping_lga, phone_number]):
                        shipping_address = Address(
                            user=self.request.user,
                            shipping_street=shipping_street,                            
                            shipping_state=shipping_state,
                            shipping_lga=shipping_lga, 
                            phone_number=phone_number
                        )
                        shipping_address.save()

                        order.shipping_address=shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'default')
                        shipping_location = form.cleaned_data.get(
                            'shipping_state')
                        if shipping_location == 'Edo':
                            shipping_fee = 500
                        else:
                            shipping_fee = 1500
                        order.shipping_fee=shipping_fee
                        order.save()
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'O':
                    return redirect('src:online', payment_option='Payment')
                elif payment_option == 'B':
                    return redirect('src:bank', payment_option='Payment')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('src:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("src:order-summary")


class OnlinePaymentView(View):
    def get(self, *args, **kwargs):
        context = {}
        return render(self.request, "main/onlinepayment.html", context)

class BankpPaymentView(View):
    def get(self, *args, **kwargs):
        context = {}
        return render(self.request, "main/bankpayment.html", context)
############################################################################################
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("src:checkout")

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("src:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("src:checkout")
############################################################################################
class ItemDetailView(DetailView):
    model = Item    
    template_name = "main/item.html"
    form = FormTypeForm() 
    context_object_name = 'item'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)         
        context['form'] = self.form      
        return context    

@login_required
def add_to_cart(request, slug):
    def namestr(**kwargs):
        bowl = []
        for k,v in kwargs.items():
            if v != None:
                bowl.append("%s = %s" % (k, v))
        return bowl 
    get_p_list = namestr(
        size = request.GET.get('size'),
        skirt_length=request.GET.get('skirt_length'),
        shirt_length=request.GET.get('shirt_length') ,
        gown_length=request.GET.get('gown_length'),
        trouser_length=request.GET.get('trouser_length')
        ) 
    item = get_object_or_404(Item, slug=slug)
    order_item, created=OrderItem.objects.get_or_create(        
        orderPref=get_p_list,
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order=order_qs[0]           
        u = OrderItem.objects.filter(orderPref=order_item.orderPref)
        u = str(u[0]).strip( ' ' ).split(']')[0]+']' 
        if  order.items.filter(item__slug=item.slug).exists():            
            if order_item.orderPref == u:
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect("src:order-summary")    
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("src:order-summary") 
    return redirect("src:order-summary") 




@login_required
def add_to_cart2(request, slug):
    def namestr(**kwargs):
        bowl = []
        for k,v in kwargs.items():
            if v != None:
                bowl.append("%s = %s" % (k, v))
        return bowl 
    get_p_list = namestr(
        size = request.GET.get('size'),
        skirt_length =  request.GET.get('skirt_length'),
        shirt_length =request.GET.get('shirt_length') ,
        gown_length =  request.GET.get('gown_length'),
        trouser_length =  request.GET.get('trouser_length')
        )    
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        orderPref = get_p_list,   
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("src:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("src:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("src:order-summary")
       

############################################################################################id, item, item_id, order, orderPref, ordered, quantity, user, user_id
@login_required
def increase_quantity(request, pk):   
    orderPref =  OrderItem.objects.get(pk=pk)
    param = str(orderPref).strip( ' ' ).split(']')[0]+']'    
    o = OrderItem.objects.all()          
    q = OrderItem.objects.get(orderPref=param)            
    for p in o:
        if p == q:           
            q.quantity += 1
            q.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("src:order-summary")

@login_required
def remove_single_item_from_cart(request, pk):
    orderPref =  OrderItem.objects.get(pk=pk)
    param = str(orderPref).strip( ' ' ).split(']')[0]+']'    
    o = OrderItem.objects.all()          
    q = OrderItem.objects.get(orderPref=param)            
    for p in o:
        if p == q and  q.quantity > 1:       
            q.quantity -= 1
            q.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("src:order-summary")
        else:
            q.quantity = 1
            q.save()
            messages.info(request, "minimum is one.")
            return redirect("src:order-summary")

@login_required
def remove_from_cart(request, pk):
    orderPref =  OrderItem.objects.get(pk=pk)
    param = str(orderPref).strip( ' ' ).split(']')[0]+']'    
    o = OrderItem.objects.all()          
    q = OrderItem.objects.get(orderPref=param)            
    for p in o:
        if p == q:       
            q.delete()          
            messages.info(request, "This item quantity was updated.")
            return redirect("src:order-summary")

############################################################################################


class OrderSummaryView(LoginRequiredMixin, View):   
    def get(self, slug, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print('======', order)
            order2 = Item.objects.all()
            context = {
                'object': order,              
                }
            return render(self.request, 'main/ordersummary.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("/")



