from rest_framework import routers
from . import views

app_name = 'administrations'

router = routers.SimpleRouter()
router.register('', views.BankInformationViewSet)

urlpatterns = router.urls
