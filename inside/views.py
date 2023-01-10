from django.shortcuts import render
from django.template import loader

from inside.models import Subscriber
from inside.senders.email import send_vas3k_email


def donate(request):
    return render(request, "donate.html")


def subscribe(request):
    if request.method != "POST":
        return render(request, "subscribe.html")

    antispam = request.POST.get("name")
    if antispam:
        return render(request, "error.html", {
            "title": "Антиспам",
            "message": "Антиспам проверка не пройдена. "
                       "Попробуйте обновить страницу и ввести email еще раз"
        })

    email = request.POST.get("email")
    if not email or "@" not in email or "." not in email:
        return render(request, "error.html", {
            "title": "Хммм",
            "message": "Это не выглядит как валидный имейл..."
        })

    subscriber, is_created = Subscriber.objects.get_or_create(
        email=email,
        defaults=dict(
            secret_hash=Subscriber.generate_secret(email),
        )
    )

    if is_created:
        opt_in_template = loader.get_template("emails/opt_in.html")
        send_vas3k_email(
            recipient=subscriber.email,
            subject=f"Подтверждение подписки",
            html=opt_in_template.render({
                "email": subscriber.email,
                "secret_hash": subscriber.secret_hash
            }),
        )

    if is_created or not subscriber.is_confirmed:
        return render(request, "message.html", {
            "title": "Нужно подтвердить почту",
            "message": "Письмо с подтверждением улетело вам на почту. "
                       "Откройте его и нажмите на кнопку, чтобы подписаться. "
                       "Это обязательно, иначе ничего приходить не будет. "
                       "Если никаких писем нет — проверьте «спам» или попробуйте другой адрес."
        })
    else:
        return render(request, "message.html", {
            "title": "Вы уже подписаны",
            "message": "Но всё равно спасибо, что проверили :)"
        })


def confirm(request, secret_hash):
    subscriber = Subscriber.objects.filter(secret_hash=secret_hash).update(is_confirmed=True)

    if subscriber:
        return render(request, "message.html", {
            "title": "Ура! Вы подписаны",
            "message": "Теперь вы будете получать на почту мои уведомления по почте"
        })
    else:
        return render(request, "error.html", {
            "title": "Неизвестный адрес",
            "message": "Указанный адрес нам не известен. Подпишитесь еще раз"
        })


def unsubscribe(request, secret_hash):
    Subscriber.objects.filter(secret_hash=secret_hash).delete()

    return render(request, "message.html", {
        "title": "Вы отписались",
        "message": "Я удалил вашу почту из базы и больше ничего вам не пришлю"
    })
