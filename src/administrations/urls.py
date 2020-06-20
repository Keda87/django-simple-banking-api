from rest_framework import routers

from . import views

app_name = 'administrations'

router = routers.SimpleRouter()
router.register('', views.BankInformationViewSet)
router.register('deposit', views.DepositViewSet, basename='deposit')
router.register('transfer', views.TransferViewSet, basename='transfer')
router.register('withdraw', views.WithdrawViewSet, basename='withdraw')

urlpatterns = router.urls
