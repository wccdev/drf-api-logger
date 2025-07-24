from rest_framework.routers import DefaultRouter

from .apps import LoggerConfig
from .constants import VIEW_REVERSE_BASENAME
from .views import ApiLogForAdminViewSet

app_name = LoggerConfig.name


router = DefaultRouter()

router.register("forAdmin", ApiLogForAdminViewSet, basename=VIEW_REVERSE_BASENAME)

urlpatterns = router.urls
