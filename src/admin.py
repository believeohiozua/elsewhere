from django.contrib import admin
from .models import Item, Category,FormType,OrderItem, Order, Address, Payment, Coupon, Refund, Profile


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True, status='Refund Granted')


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    # 'ordered',
                    # 'being_delivered',
                    # 'received',
                    # 'refund_requested',
                    # 'refund_granted',
                    'shipping_address',    
                    'status',              
                    'payment',
                    'coupon',
                    'shipping_fee',
                    'get_total'
                    ]
    list_display_links = [
        'user',
        'shipping_address',        
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'shipping_street',      
        'shipping_state',
        'shipping_lga',       
        'default'
    ]
    list_filter = ['default', 'shipping_state', 'shipping_lga']
    search_fields = ['user', 'shipping_street', 'shipping_state', 'shipping_lga']

class ProfileAdmin(admin.ModelAdmin):
    list_display = [
            'user',            
            'phone_number',
            'gender',
            'gender',
            
    ]

class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'get_item_name',
        'user',              
        'quantity',
        'orderPref', 
        'ordered',        
    ]


admin.site.register(Item, ItemAdmin)
admin.site.register(Category)
admin.site.register(FormType)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Profile, ProfileAdmin)