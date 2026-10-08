from django.db import models


class Athlete(models.Model):
    """Спортсмен, хранящийся в базе данных."""

    name = models.CharField(max_length=100, verbose_name='ФИО')
    sport = models.CharField(max_length=50, verbose_name='Вид спорта')
    age = models.IntegerField(verbose_name='Возраст')
    country = models.CharField(max_length=50, verbose_name='Страна')
    achievements = models.TextField(blank=True, verbose_name='Достижения')

    class Meta:
        verbose_name = 'Спортсмен'
        verbose_name_plural = 'Спортсмены'

    def __str__(self):
        return self.name
