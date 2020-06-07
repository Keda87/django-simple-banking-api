from rest_framework import routers

from . import views

app_name = 'administrations'

router = routers.SimpleRouter()
router.register('', views.BankInformationViewSet)
router.register('deposit', views.DepositViewSet, base_name='deposit')
router.register('transfer', views.TransferViewSet, base_name='transfer')
router.register('withdraw', views.WithdrawViewSet, base_name='withdraw')

urlpatterns = router.urls
