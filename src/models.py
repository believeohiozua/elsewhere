from django.db.models.signals import post_save, pre_save
from allauth.account.signals import user_signed_up
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.utils.text import slugify
from django_resized import ResizedImageField
from django_countries.fields import CountryField
from django.contrib.auth import get_user_model
User = get_user_model()
 
LABEL_CHOICES = (
    ('NEW', 'NEW'), 
    ('HOT', 'HOT'), 
     ('TREND', 'TREND'),
    
) 
AVALABILITY_CHOICES = (
    ('In Stock', 'in_stock'),
    ('Out of Stock', 'out_of_stock'),     
)

 

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)  
    phone_number= models.CharField(max_length=100, blank=True, null=True)
    gender=models.CharField(max_length=100, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)
    profile_photo = ResizedImageField(size=[80, 80], upload_to='profile', blank=True, null=True, force_format='PNG') 

   

    def __str__(self):
        return self.pk
    
    def get_absolute_url(self):
        return reverse('src:profile', kwargs={
             'pk': self.pk
        })
#******************
def ProfileCallback(sender, request, user, **kwargs):
    userProfile, is_created = Profile.objects.get_or_create(user=user)
    if is_created:          
        userProfile.phone_number=user.phone_number 
        userProfile.gender=user.gender 
        userProfile.save()
user_signed_up.connect(ProfileCallback)
# pre_save.connect(ProfileCallback, sender=settings.AUTH_USER_MODEL)

# def profile_receiver(sender, **kwargs):   
#     userProfile, created = Profile.objects.create(user=settings.AUTH_USER_MODEL)
#     if created:        
#         userProfile.first_name = user.first_name
#         userProfile.last_name = user.last_name      
#         # userProfile.phone_number = user.phone_number 
#         # userProfile.gender = user.gender 
#         userProfile.save()
# pre_save.connect(profile_receiver, sender=settings.AUTH_USER_MODEL)

class Category(models.Model):
    category = models.CharField(max_length=20)   
    def __str__(self):
        return self.category


class FormType(models.Model):
    formtype = models.CharField(max_length=20)   
    def __str__(self): 
        return self.formtype

class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True)   
    form_type = models.ManyToManyField(FormType, blank=True)    
    label = models.CharField(choices=LABEL_CHOICES, max_length=20, blank=True, null=True)
    availability =  models.CharField(choices=AVALABILITY_CHOICES, max_length=20, blank=True, null=True)    
    brand =  models.CharField(max_length=100)
    quantity = models.IntegerField() 
    description = models.TextField()    
    image = ResizedImageField(size=[215, 215], upload_to='items', force_format='PNG')    
    slug = models.SlugField(blank=True, null=True, default="Please-Leave-Blank")

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("src:item-detail", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("src:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("src:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def get_item_id(self):
        return str(int(self.pk + 100000))
    
    def get_discount_percent(self):
        fraction =  (self.price - self.discount_price)
        percent = (fraction/self.price)*100
        return int(percent)

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    orderPref = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return f"{self.orderPref} of {self.item.name}"

    def get_item_name(self):
        return f"{self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return int(self.quantity * self.item.discount_price)

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def get_quantity(self):        
        return self.quantity

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True) 
    shipping_fee = models.IntegerField(blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    status=models.CharField(max_length=100, blank=True, null=True) 


    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        if self.shipping_fee:
            total += int(self.shipping_fee)
        return total

    def get_total_quantity(self):
        quantity = 0
        for order_item in self.items.all():
            quantity += order_item.get_quantity()    
        return quantity

    def save(self, *args, **kwargs):
        if not self.ordered:
            value = 'Not Ordered'
            self.status = value
            super().save(*args, **kwargs)
        else: 
            value = 'Ordered'
            self.status = value
            super().save(*args, **kwargs)
        if self.being_delivered:
            value = 'Being Deliverd'
            self.status = value
            super().save(*args, **kwargs)
        elif self.received:
            value = 'Received'
            self.status = value
            super().save(*args, **kwargs)
        elif self.refund_requested:
            value = 'Refund Requested'
            self.status = value
            super().save(*args, **kwargs)
        elif self.refund_granted:
            value = 'Refund Granted'
            self.status = value
            super().save(*args, **kwargs)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)
class Address(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    shipping_street=models.CharField(max_length=1000, blank=True, null=True)
    shipping_state=models.CharField(max_length=100, blank=True, null=True)   
    shipping_lga=models.CharField(max_length=100, blank=True, null=True)
    phone_number=models.CharField(max_length=100, blank=True, null=True)   
    default = models.BooleanField(default=False)

    # address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    # country = CountryField(multiple=False)

    def __str__(self):
        return f"{self.user.username} from  {self.shipping_state} "
        # return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


# def profile_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         userprofile = Profile.objects.create(user=instance)
# post_save.connect(profile_receiver, sender=settings.AUTH_USER_MODEL)