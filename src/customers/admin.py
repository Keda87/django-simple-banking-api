from django.contrib import admin

from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'sex', 'identity_number',
    ]
    search_fields = [
        'guid', 'user__username', 'user__email', 'user__first_name',
        'user__last_name',
    ]
    list_filter = ['sex']


admin.site.register(Customer, CustomerAdmin)
