from django.shortcuts import render
from django.http.response import JsonResponse
from .models import User, Favourites
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt


def get_user(request, telegram_id) -> JsonResponse:
    """
    Получение данных о пользователе, если пользователя
    нет в БД - выбрасывает 502 статус ответа
    """
    try:
        user = User.objects.get(telegram_id=telegram_id)
    except ObjectDoesNotExist:
        response = {
            'status': 'false',
            'message': 'user not found'}
        return JsonResponse(response, status=502)

    response = {
        'user_id': user.telegram_id,
        'user_fullname': user.fullname,
        'user_phone_number': user.phone_number
    }
    return JsonResponse(
        response,
        status=200,
        json_dumps_params={'ensure_ascii': False}
    )


@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        user_telegram_id = request.POST.get('user_tg_id')
        user_fullname = request.POST.get('user_fullname')
        user_phone_number = request.POST.get('user_phone_number')

        user = User.objects.create(
            telegram_id=user_telegram_id,
            fullname=user_fullname,
            phone_number=user_phone_number
        )

        Favourites.objects.create(user=user)

        response = {
            'status': 'true',
            'message': 'user created'
        }
        return JsonResponse(response, status=200)

    response = {
        'status': 'false',
        'message': 'Not supported method'
    }
    return JsonResponse(response, status=501)
