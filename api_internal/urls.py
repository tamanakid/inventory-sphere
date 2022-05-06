from django.urls import path, include

from . import views


urlpatterns = [
    path('location_levels/', views.LocationLevelsListView.as_view(), name='internal__location_levels_list'),
    #views.PatientViewSet.reverse_action(views.PatientViewSet.get_residence_users.url_name, args=['1'])
]