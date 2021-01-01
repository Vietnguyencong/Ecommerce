from django.contrib import admin

from .models import * 

# allow admin to edit those models

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)