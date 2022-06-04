from rest_framework.pagination import PageNumberPagination


class APIPaginator(PageNumberPagination):
    page_size_query_param = 'size'  # items per page
