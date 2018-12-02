from rest_framework import routers

from . import views

app_name = 'administrations'

router = routers.SimpleRouter()
router.register('', views.BankInformationViewSet)
router.register('deposit', views.DepositViewSet, base_name='deposit')

urlpatterns = router.urls
