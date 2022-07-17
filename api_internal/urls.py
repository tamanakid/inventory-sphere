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

    path('categories/', views.CategoriesListView.as_view(), name='internal__categories_list'),
    path('categories/tree/', views.CategoriesTreeView.as_view(), name='internal__categories_tree'),
    path('categories/<int:id>', views.CategoriesView.as_view(), name='internal__categories'),
    path('categories/<int:id>/children/', views.CategoriesChildrenView.as_view(), name='internal__categories_children'),
    path('categories/delete/', views.CategoriesDeleteView.as_view(), name='internal__categories_delete'),

    path('location_levels/', views.LocationLevelsListView.as_view(), name='internal__location_levels_list'),
    path('location_levels/<int:id>', views.LocationLevelView.as_view(), name='internal__location_levels'),
    path('location_levels/delete/', views.LocationLevelsDeleteView.as_view(), name='internal__location_levels_delete'),

    path('locations/', views.LocationsListView.as_view(), name='internal__locations_list'),
    path('locations/tree/', views.LocationsTreeView.as_view(), name='internal__locations_tree'),
    path('locations/<int:id>', views.LocationsView.as_view(), name='internal__locations'),
    path('locations/delete/', views.LocationsDeleteView.as_view(), name='internal__locations_delete'),

    path('products/', views.ProductsListView.as_view(), name='internal__products_list'),
    path('products/<int:id>', views.ProductsView.as_view(), name='internal__products'),
    path('products/delete/', views.ProductsDeleteView.as_view(), name='internal__products_delete'),

    path('product_skus/', views.ProductSkusListView.as_view(), name='internal__product_skus_list'),
    path('product_skus/<int:id>', views.ProductSkusView.as_view(), name='internal__product_skus'),
    path('product_skus/delete/', views.ProductSkusDeleteView.as_view(), name='internal__product_skus_delete'),

    # Stock
    path('stock_items/', views.StockItemsListView.as_view(), name='internal__stock_items_list'),
    path('stock_items/bulk_add/', views.StockItemsBulkAddView.as_view(), name='internal__stock_items_bulk_add'),
    path('stock_items/bulk_update/', views.StockItemsBulkUpdateView.as_view(), name='internal__stock_items_bulk_update'),
    path('stock_items/remove/', views.StockItemsRemoveView.as_view(), name='internal__stock_items_remove'),

    #views.PatientViewSet.reverse_action(views.PatientViewSet.get_residence_users.url_name, args=['1'])
]