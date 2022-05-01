from django.urls import path, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register('location_levels', views.LocationLevelViewSet)


print(router.get_urls())

urlpatterns = [
    path('', include(router.urls)),
    #views.PatientViewSet.reverse_action(views.PatientViewSet.get_residence_users.url_name, args=['1'])
]