from django.urls import path, include

app_name = 'router_v1'
urlpatterns = [
    path('customers/', include('customers.urls', namespace='customers')),
    path('accounts/', include('administrations.urls', namespace='accounts')),
]