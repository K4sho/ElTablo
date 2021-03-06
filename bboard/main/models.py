from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from .utilities import send_activation_notification, get_timestamp_path, send_new_comment_notification
from django.db.models.signals import post_save


class AdvUser(AbstractUser):
    """Модель расширенного пользователя"""
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
    send_messages = models.BooleanField(default=True, verbose_name='Слать оповещения о новых комментариях?')

    """Явное удаление объявлений, оставленных пользователем, при удалении пользователя"""
    def delete(self, *args, **kwargs):
        for bb in self.bb_set.all():
            bb.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Rubric(models.Model):
    """Модель рубрик"""
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='Название')
    order = models.IntegerField(default=0, db_index=True, verbose_name='Порядок')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT,
                                     null=True, blank=True, verbose_name='Надрубрика')


class SuperRubricManager(models.Manager):
    """Диспетчер записей"""
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    """Модель надрубрик"""
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')  # Порядок сортировки
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'


class SubRubricManager(models.Manager):
    """Диспетчер записей подрубрик"""
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    """Модель подрубрик"""
    objects = SubRubricManager()

    def __str__(self):
        return '%s - %s' % (self.super_rubric.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'


class Bb(models.Model):
    """Модель объявления"""
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT, verbose_name='Рубрика')
    title = models.CharField(max_length=40, verbose_name='Товар')
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(default=0, verbose_name='Цена')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображения')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    def delete(self, *args, **kwargs):
        """Перед тем как удалить запись - удаляем все иллюстрации, связанные с этой записью"""
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-created_at']


class Comment(models.Model):
    """Модель комментариев пользователей"""
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить на экран?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['created_at']


class AdditionalImage(models.Model):
    """Модель иллюстраций"""
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

    class Meta:
        verbose_name_plural = 'Дополнительные иллюстрации'
        verbose_name = 'Дополнительная иллюстрация'


# Объявляем сигнал
user_registrated = Signal(providing_args=['instance'])


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


# Привязываем к сигналу обработчик
user_registrated.connect(user_registrated_dispatcher)


def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].bb.author
    # Нужно еще проверить не запретил ли пользователь отправлять уведомления
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])


# Привязываем к сигналу обработчик
post_save.connect(post_save_dispatcher, sender=Comment)
