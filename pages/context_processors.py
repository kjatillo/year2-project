from services.models import Category


def category_links(request):
    category_links = Category.objects.all()

    return {'category_links': category_links}
