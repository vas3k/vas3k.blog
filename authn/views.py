import logging
from urllib.parse import urlencode, quote, urlparse

import jwt
from django.conf import settings
from django.contrib.auth import logout, login
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse

from authn import club, patreon
from authn.exceptions import PatreonException
from users.models import User

log = logging.getLogger(__name__)


def log_in(request):
    return render(request, "users/login.html")


def log_out(request):
    logout(request)
    return redirect("index")


def login_club(request):
    if request.user.is_authenticated:
        return redirect("profile")

    goto = request.GET.get("goto")
    params = urlencode({
        "app_id": "vas3k_blog",
        "redirect": f"https://{request.get_host()}/auth/club_callback/" + (f"?goto={quote(goto)}" if goto else "")
    })
    return redirect(f"{settings.CLUB_AUTH_URL}?{params}")


def club_callback(request):
    token = request.GET.get("jwt")
    if not token:
        return render(request, "error.html", {
            "title": "Что-то пошло не так",
            "message": "При авторизации потерялся токен. Попробуйте войти еще раз."
        })

    try:
        payload = jwt.decode(token, settings.JWT_PUBLIC_KEY, algorithms=[settings.JWT_ALGORITHM])
    except (jwt.DecodeError, jwt.ExpiredSignatureError) as ex:
        log.error(f"JWT token error: {ex}")
        return render(request, "error.html", {
            "title": "Что-то сломалось",
            "message": "Неправильный ключ. Наверное, что-то сломалось. Либо ты ХАКИР!!11"
        })

    user_slug = payload["user_slug"]
    club_profile = club.parse_membership(user_slug, token)
    if not club_profile or not club_profile.get("user"):
        return render(request, "error.html", {
            "message": f"Член Клуба с именем {user_slug} не найден. "
                       "<a href=\"https://vas3k.club\">Попробуйте</a> войти в свой "
                       "аккаунт и потом авторизоваться здесь снова."
        })

    if club_profile["user"]["payment_status"] != "active":
        return render(request, "error.html", {
            "message": "Ваша подписка истекла. "
                       "<a href=\"https://vas3k.club\">Продлите</a> её здесь."
        })

    user = User.objects.filter(Q(email=payload["user_email"]) | Q(vas3k_club_slug=payload["user_slug"])).first()
    if user:
        user.avatar = club_profile["user"]["avatar"]
        user.vas3k_club_slug = payload["user_slug"]
        if not user.email:
            user.email = payload["user_email"]
        user.country = club_profile["user"]["country"]
        user.city = club_profile["user"]["city"]
        user.save()
    else:
        user = User.objects.create_user(
            vas3k_club_slug=payload["user_slug"],
            avatar=club_profile["user"]["avatar"],
            username=club_profile["user"]["full_name"][:20],
            email=payload["user_email"],
        )

    login(request, user)

    goto = request.GET.get("goto")
    if goto and urlparse(goto).netloc == request.get_host():
        redirect_to = goto
    else:
        redirect_to = reverse("profile")

    return redirect(redirect_to)


def login_patreon(request):
    if request.user.is_authenticated:
        return redirect("profile")

    state = {}
    goto = request.GET.get("goto")
    if goto:
        state["goto"] = goto

    query_string = urlencode({
        "response_type": "code",
        "client_id": settings.PATREON_CLIENT_ID,
        "redirect_uri": f"https://{request.get_host()}/auth/patreon_callback/",
        "scope": settings.PATREON_SCOPE,
        "state": urlencode(state) if state else ""
    })
    return redirect(f"{settings.PATREON_AUTH_URL}?{query_string}")


def patreon_callback(request):
    code = request.GET.get("code")
    if not code:
        return render(request, "error.html", {
            "message": "Что-то сломалось между нами и патреоном. Так бывает. Попробуйте залогиниться еще раз."
        })

    try:
        auth_data = patreon.fetch_auth_data(
            code=code,
            original_redirect_uri=f"https://{request.get_host()}/auth/patreon_callback/"
        )
        user_data = patreon.fetch_user_data(auth_data["access_token"])
    except PatreonException as ex:
        if "invalid_grant" in str(ex):
            return render(request, "error.html", {
                "message": "Тут такое дело. Авторизация патреона — говно. "
                           "Она не сразу понимает, что вы стали моим патроном и отдаёт мне ошибку. "
                           "Саппорт молчит, так что единственный рабочий вариант — вернуться и авторизоваться еще раз. "
                           "Обычно тогда срабатывает."
            })

        return render(request, "error.html", {
            "message": "Не получилось загрузить ваш профиль с серверов патреона. "
                       "Попробуйте еще раз, наверняка оно починится. "
                       f"Но если нет, то вот текст ошибки, с которым можно пожаловаться мне в личку: {ex}"
        })

    membership = patreon.parse_my_membership(user_data)
    if not membership:
        return render(request, "error.html", {
            "message": "Надо быть активным патроном, чтобы комментировать на сайте.<br>"
                       "<a href=\"https://www.patreon.com/join/vas3k\">Станьте им здесь!</a>"
        })

    user = User.objects\
        .filter(Q(email=user_data["data"]["attributes"]["email"]) | Q(patreon_id=user_data["data"]["id"]))\
        .first()

    if user:
        if not user.patreon_id:
            return render(request, "error.html", {
                "message": "Пользователь с таким имейлом есть, но он не с Патреона. "
                           "Войдите другим способом."
            })
    else:
        user = User.objects.create_user(
            patreon_id=user_data["data"]["id"],
            username=str(user_data["data"]["attributes"]["full_name"])[:20],
            email=user_data["data"]["attributes"]["email"],
        )

    login(request, user)

    goto = request.GET.get("goto")
    if goto and urlparse(goto).netloc == request.get_host():
        redirect_to = goto
    else:
        redirect_to = reverse("profile")

    return redirect(redirect_to)
