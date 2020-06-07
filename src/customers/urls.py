from rest_framework import routers
from . import views

app_name = 'customers'

router = routers.SimpleRouter()
router.register('', views.CustomerViewSet)

urlpatterns = router.urls