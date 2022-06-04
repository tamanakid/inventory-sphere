from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from _app_config.custom_auth import (
    CustomTokenObtainPairView,
    # CustomTokenRefreshView,
)

from . import views


urlpatterns = [
    # Auth
    # path('auth/token/', TokenObtainPairView.as_view(), name='internal__token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='internal__token_refresh'),
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='internal__token_obtain_pair'),
    # path('auth/refresh/', CustomTokenRefreshView.as_view(), name='internal__token_refresh'),

    # Custom
    path('attributes/', views.AttributesListView.as_view(), name='internal__attributes_list'),
    path('attributes/<int:id>', views.AttributesView.as_view(), name='internal__attributes'),
    path('attributes/delete/', views.AttributesDeleteView.as_view(), name='internal__attributes_delete'),
    path('attribute_values/', views.AttributeValuesListView.as_view(), name='internal__attribute_values_list'),
    path('attribute_values/<int:id>', views.AttributeValuesView.as_view(), name='internal__attribute_values'),
    path('attribute_values/delete/', views.AttributeValuesDeleteView.as_view(), name='internal__attribute_values_delete'),
    path('location_levels/', views.LocationLevelsListView.as_view(), name='internal__location_levels_list'),
    path('location_levels/<int:id>', views.LocationLevelView.as_view(), name='internal__location_levels'),
    path('locations/', views.LocationsListView.as_view(), name='internal__locations_list'),
    path('locations/<int:id>', views.LocationsView.as_view(), name='internal__locations'),


    #views.PatientViewSet.reverse_action(views.PatientViewSet.get_residence_users.url_name, args=['1'])
]