from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """后台统一分页处理类"""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20

