from django.shortcuts import render
from django.template import loader
from django.utils.translation import gettext_lazy as _

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
            "title": _("Антиспам"),
            "message": _("Антиспам проверка не пройдена. "
                         "Попробуйте обновить страницу и ввести email еще раз")
        })

    email = request.POST.get("email")
    if not email or "@" not in email or "." not in email:
        return render(request, "error.html", {
            "title": _("Хммм"),
            "message": _("Это не выглядит как валидный имейл...")
        })

    subscriber, is_created = Subscriber.objects.get_or_create(
        email=email,
        defaults=dict(
            secret_hash=Subscriber.generate_secret(email),
            lang=request.LANGUAGE_CODE,
        )
    )

    if is_created:
        opt_in_template = loader.get_template("emails/opt_in.html")
        send_vas3k_email(
            subscriber=subscriber,
            subject=_("Подтверждение подписки"),
            html=opt_in_template.render({
                "email": subscriber.email,
                "secret_hash": subscriber.secret_hash
            }),
            force=True,
        )

    if is_created or not subscriber.is_confirmed:
        return render(request, "message.html", {
            "title": _("Нужно подтвердить почту"),
            "message": _("Письмо с подтверждением улетело вам на почту. "
                       "Откройте его и нажмите на кнопку, чтобы подписаться. "
                       "Это обязательно, иначе ничего приходить не будет. "
                       "Если никаких писем нет — проверьте «спам» или попробуйте другой адрес.")
        })
    else:
        return render(request, "message.html", {
            "title": _("Вы уже подписаны"),
            "message": _("Но всё равно спасибо, что проверили :)")
        })


def confirm(request, secret_hash):
    subscriber = Subscriber.objects.filter(secret_hash=secret_hash).update(is_confirmed=True)

    if subscriber:
        return render(request, "message.html", {
            "title": _("Ура! Вы подписаны"),
            "message": _("Теперь вы будете получать на почту мои уведомления по почте")
        })
    else:
        return render(request, "error.html", {
            "title": _("Неизвестный адрес"),
            "message": _("Указанный адрес нам не известен. Подпишитесь еще раз")
        })


def unsubscribe(request, secret_hash):
    Subscriber.objects.filter(secret_hash=secret_hash).delete()

    return render(request, "message.html", {
        "title": _("Вы отписались"),
        "message": _("Я удалил вашу почту из базы и больше ничего вам не пришлю")
    })
