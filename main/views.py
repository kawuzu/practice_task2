from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .forms import CustomUserCreationForm, StatusChangeForm, CategoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from .forms import DesignRequestForm
from django.contrib.auth.decorators import login_required
from .models import DesignRequest, Category
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import DesignRequest

# Create your views here.
def home(request):
    # авторизован ли пользователь
    if request.user.is_authenticated:
        welcome_message = f"Привет, {request.user.username}!"
    else:
        welcome_message = ("Здравствуй, гость! Мы - дизайн-студия DesignPro! "
                           "Пожалуйста, войдите или зарегистрируйтесь, чтобы мы помогли воплотить ваши самые смелые мечты о дизайне!")

    return render(request, 'main/index.html', {'welcome_message': welcome_message})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            # Создание нового пользователя
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)  # Вход после регистрации
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect('home')  # Перенаправление на главную страницу
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@sync_to_async
def is_username_taken(username):
    return User.objects.filter(username=username).exists()

async def check_username(request):
    username = request.GET.get('username')
    if username:
        is_taken = await is_username_taken(username)
        return JsonResponse({'is_taken': is_taken})
    return JsonResponse({'error': 'Username not provided'}, status=400)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Неверный логин или пароль.')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def create_request(request):
    if request.method == 'POST':
        form = DesignRequestForm(request.POST, request.FILES)
        if form.is_valid():
            design_request = form.save(commit=False)
            design_request.user = request.user
            design_request.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = DesignRequestForm()

    return render(request, 'main/create_request.html', {'form': form})


# Страница списка всех заявок пользователя
@login_required  #только авторизованные пользователи могут просматривать свои заявки
def my_requests(request):
    #все заявки текущего пользователя: сначала важные, затем остальные
    requests = DesignRequest.objects.filter(user=request.user).order_by('-is_important', '-created_at')

    return render(request, 'main/my_requests.html', {'requests': requests})

# Страница с подробной информацией о заявке
def request_detail(request, request_id):
    # Получаем заявку по id
    design_request = get_object_or_404(DesignRequest, id=request_id)

    return render(request, 'main/request_detail.html', {'request': design_request})

@login_required
def delete_request(request, id):
    request_to_delete = get_object_or_404(DesignRequest, id=id)

    if request_to_delete.user == request.user:
        request_to_delete.delete()
        return redirect('my_requests')
    else:
        return redirect('home')

@staff_member_required  #доступ только для администратора
def all_requests(request):
    requests = DesignRequest.objects.all()  #все заявки
    return render(request, 'main/all_requests.html', {'requests': requests})

@staff_member_required
def change_request_status(request, request_id):
    user_request = get_object_or_404(DesignRequest, id=request_id)


    if request.method == 'POST':
        form = StatusChangeForm(request.POST, instance=user_request)
        if form.is_valid():
            form.save()
            messages.success(request, f"Статус заявки '{user_request.title}' изменен!")
            return redirect('main:admin_view_requests')
    else:
        form = StatusChangeForm(instance=user_request)

    return render(request, 'main/change_status.html', {'form': form, 'request': user_request})

@staff_member_required
def change_request_status(request, request_id):

    design_request = get_object_or_404(DesignRequest, id=request_id)

    if request.method == 'POST':
        form = StatusChangeForm(request.POST, instance=design_request)
        if form.is_valid():
            form.save()
            messages.success(request, f"Статус заявки '{design_request.title}' успешно изменен!")
            return redirect('all_requests')
    else:
        form = StatusChangeForm(instance=design_request)

    return render(request, 'main/change_status.html', {'form': form, 'design_request': design_request})


@staff_member_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория успешно добавлена!")
            return redirect('all_categories')
    else:
        form = CategoryForm()

    return render(request, 'main/create_category.html', {'form': form})

@staff_member_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Категория '{category.name}' успешно обновлена!")
            return redirect('all_categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'main/edit_category.html', {'form': form, 'category': category})


@staff_member_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, f"Категория '{category.name}' удалена!")
    return redirect('all_categories')

def all_categories(request):
    categories = Category.objects.all()
    return render(request, 'main/all_categories.html', {'categories': categories})