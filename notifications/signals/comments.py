import telegram
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.models import Comment
from notifications.telegram.bot import bot


@receiver(post_save, sender=Comment)
def create_comment(sender, instance, created, **kwargs):
    comment = instance
    post = comment.post

    link = f"https://{settings.APP_HOST}/{post.type}/{post.slug}/"

    if comment.block:
        link += f"#block-{comment.block}-{comment.id}"
    else:
        link += f"#comment-{comment.id}"

    full_text = f"💬 <b>{comment.author_name}</b> ➜ <a href='{link}'>{post.title}</a>:\n\n{comment.text[:2000]}"

    bot.send_message(
        chat_id=settings.TELEGRAM_MAIN_CHAT_ID,
        text=full_text,
        parse_mode=telegram.ParseMode.HTML,
        disable_web_page_preview=True
    )
