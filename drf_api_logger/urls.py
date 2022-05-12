from rest_framework.routers import SimpleRouter

from .views import APILoggerViewSet

router = SimpleRouter()

router.register("apilogs", APILoggerViewSet, basename='apilogs')
urlpatterns = router.urls
