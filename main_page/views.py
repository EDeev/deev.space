from django.shortcuts import render


# ВЫВОД СТРАНИЦ ОШИБОК
def custom_page_not_found_view(request, exception):
    return render(request, "errors/404.html", {})


def custom_error_view(request, exception=None):
    return render(request, "errors/500.html", {})


def custom_permission_denied_view(request, exception=None):
    return render(request, "errors/403.html", {})


def custom_bad_request_view(request, exception=None):
    return render(request, "errors/400.html", {})


# ПЕРЕХОДЫ ПО САЙТУ
def index(request):
    return render(request, 'unfold/index.html')

