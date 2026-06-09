from .models import Category


def nav(request):
    return {
        'nav_categories': Category.objects.all(),
    }
