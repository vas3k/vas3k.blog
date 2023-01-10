from django.http import HttpResponse
from django.shortcuts import render, redirect

from users.forms import UserEditForm


def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserEditForm(instance=request.user)

    return render(request, "users/profile.html", {
        "form": form,
    })


def robots(request):
    lines = [
        "User-agent: *",
        "Host: https://vas3k.blog",
        "Disallow: /clickers/",
        "Disallow: /auth/",
        "Clean-param: comment_order&goto /",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
