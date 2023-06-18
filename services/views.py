from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Avg
from .models import Category, Service, Review
from .forms import ReviewForm

class ServiceCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_service'
    model = Service
    template_name = 'service_new.html'
    fields = [
        'name',
        'description',
        'category',
        'price',
        'image',
        'job_limit',
        'available',
    ]

    def form_valid(self, form):
        form.instance.provider = self.request.user

        return super().form_valid(form)

def service_list(request, category_id=None):
    category = None
    services = Service.objects.filter(available=True)
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        services = Service.objects.filter(category=category, available=True)

    paginator = Paginator(services, 16)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        services = paginator.page(page)
    except (EmptyPage,InvalidPage):
        services = paginator.page(paginator.num_pages)

    return render(request, 'category.html',{'category':category, 'services':services})

def provider_service_list(request):
    category = None
    services = Service.objects.filter(provider=request.user)

    paginator = Paginator(services, 18)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        services = paginator.page(page)
    except (EmptyPage,InvalidPage):
        services = paginator.page(paginator.num_pages)

    return render(request, 'service_provider.html',{'category':category, 'services':services})


def service_detail(request, category_id, service_id):
    service = get_object_or_404(Service, category_id=category_id, id=service_id)
    reviews = service.review_set.all().order_by('-created')
    average = reviews.aggregate(Avg("rating"))["rating__avg"]
    if average == None:
        average = 0
    average = round(average, 1)
    return render(request, 'service.html', {'service':service, 'reviews':reviews, 'average':average})

def submit_review(request, service_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = Review.objects.get(user=request.user, service_id=service_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        
        except Review.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = Review()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.service_id = service_id
                data.user = request.user
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
        
class ServiceUpdateView(UpdateView):
    model = Service
    template_name = 'service_edit.html'
    fields = [
        'name',
        'description',
        'category',
        'price',
        'image',
        'job_limit',
        'available',
    ]
    pk_url_kwarg = 'service_id'

class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'service_delete.html'
    success_url = reverse_lazy('home')
    pk_url_kwarg = 'service_id'
