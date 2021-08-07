import datetime as dt

#  импортируем CreateView, чтобы создать ему наследника
from django.views.generic import CreateView

#  функция reverse_lazy позволяет
#  получить URL по параметру "name" функции path()
#  берём, тоже пригодится
from django.urls import reverse_lazy

#  импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    #  где signup — это параметр "name" в path()
    success_url = reverse_lazy("index")
    template_name = "signup.html"


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    current_datetime = dt.datetime.now()
    year = current_datetime.year
    return {
        'year': year
    }
