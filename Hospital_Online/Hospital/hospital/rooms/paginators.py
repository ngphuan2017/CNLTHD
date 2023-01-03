from rest_framework.pagination import PageNumberPagination

class KhoaPaginator(PageNumberPagination):
    page_size = 10
