from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


def homepage(request):
    return render(request=request, template_name="users/home.html")


def register_request(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Успешно зарегистрированы.")
            return redirect("users:homepage")
        messages.error(request, "Зарегистрироваться не удалось. Неверная информация.")
    else:
        form = CustomUserCreationForm()
    return render(request=request, template_name="users/register.html", context={"register_form": form})


class TestAcces(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Ok'}
        return Response(content)
