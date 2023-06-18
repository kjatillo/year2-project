from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView
from services.models import Category, Service


class SearchResultsListView(ListView):
    model = Service
    context_object_name = 'search_result'
    template_name = 'search_result.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        
        return Service.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(category__name__icontains=query)
        )

    def get_context_data(self, **kwargs):
        context = super(SearchResultsListView, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        
        return context


def filterView(request):
    qs = Service.objects.all()
    service_contains_query = request.GET.get('service_contains')
    provider_contains_query = request.GET.get('service_provider_contains')
    service_or_provider_query = request.GET.get('service_or_provider')
    category = request.GET.get('category')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    date_posted_min = request.GET.get('date_min')
    date_posted_max = request.GET.get('date_max')

    if service_contains_query != '' and service_contains_query is not None:
        qs = qs.filter(name__icontains=service_contains_query)
    elif provider_contains_query != '' and provider_contains_query is not None:
        qs = qs.filter(provider__username__icontains=provider_contains_query)
    elif service_or_provider_query != '' and service_or_provider_query is not None:
        qs = qs.filter(
            Q(name__icontains=service_or_provider_query) | Q(provider__username__icontains=service_or_provider_query)
        ).distinct()

    if category != '---' and category != '' and category is not None:
        qs = qs.filter(category__name=category)

    if price_min != '' and price_min is not None:
        qs = qs.filter(price__gte=price_min)

    if price_max != '' and price_max is not None:
        qs = qs.filter(price__lte=price_max)

    if date_posted_min != '' and date_posted_min is not None:
        qs = qs.filter(created__gte=date_posted_min)
    
    if date_posted_max != '' and date_posted_max is not None:
        qs = qs.filter(created__lte=date_posted_max)

    context = {'queryset': qs}

    return render(
        request,
        'advanced_search_result.html',
        context
    )
