from rest_framework.routers import DefaultRouter

from .views import UserViewSet

router = DefaultRouter()
router.register("utilisateurs", UserViewSet, basename="utilisateur")

urlpatterns = router.urls
