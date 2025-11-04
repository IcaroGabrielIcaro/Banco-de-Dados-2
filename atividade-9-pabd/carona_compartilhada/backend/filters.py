import django_filters
from .models import Carona

class CaronaFilter(django_filters.FilterSet):
    preco_min = django_filters.NumberFilter(field_name="preco", lookup_expr='gte')
    preco_max = django_filters.NumberFilter(field_name="preco", lookup_expr='lte')
    data = django_filters.DateFilter(field_name="data", lookup_expr='exact')
    origem = django_filters.CharFilter(field_name="origem", lookup_expr='icontains')
    destino = django_filters.CharFilter(field_name="destino", lookup_expr='icontains')

    class Meta:
        model = Carona
        fields = ['preco_min', 'preco_max', 'data', 'origem', 'destino']
