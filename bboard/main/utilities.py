from django.template.loader import render_to_string
from django.core.signing import Signer
from bboard.settings import ALLOWED_HOSTS
from datetime import datetime
from os.path import splitext


# Создание цифровой подписи
signer = Signer()


def send_activation_notification(user):
    """
    Чтобы сформировать интернет-адрес, ведущий на страницу подтверждения актива­
    ции, нам понадобится, во-первых, домен, на котором находится наш сайт, а во­
    вторых, некоторое значение, уникально идентифицирующее только что зарегист­
    рированного пользователя и при этом устойчивое к попыткам его подделать.

    Домен мы можем извлечь из списка разрешенных доменов, который записан в па­
    раметре ALLOWED_HOSTS настроек проекта. В нашем случае мы используем самый
    первый домен, что присутствует в списке. Если же список доменов пуст, мы задей­
    ствуем интернет-адрес, используемый отладочным веб-сервером Django.
    """
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'
    context = {'user': user, 'host': host, 'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    user.email_user(subject, body_text)


def get_timestamp_path(instance, filename):
    """Функция генерирует имена сохраняемых в модели выгруженных файлов"""
    return '%s%s' % (datetime.now().timestamp(), splitext(filename)[1])
