import uuid
from django.db import models
from django.urls import reverse


class Counters(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    time = models.DateTimeField(verbose_name='Время')
    lengths = models.TextField(verbose_name='Значения длины, м', blank=True, null=True)  # This field type is a guess.
    connection_counters = models.TextField(verbose_name='Наличие связи', blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'counters'
        verbose_name = 'Счетчик'
        verbose_name_plural = 'Счетчики'

    def __str__(self):
        return str(self.time)


class LinesStatistics(models.Model):
    # id = models.IntegerField(primary_key=True, editable=False)
    date = models.DateTimeField(verbose_name='Дата' )
    made_kabel = models.TextField(verbose_name='Произведено кабеля, км', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lines_statistics'
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'

    def __str__(self):
        return str(self.date)


class Lines(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    line_number = models.IntegerField(verbose_name='№ линии', unique=True)
    name = models.CharField(verbose_name='Имя линии', unique=True)
    pseudonym = models.CharField(verbose_name='Отображаемое имя линии', unique=True)
    port = models.CharField(verbose_name='Порт')
    modbus_adr = models.IntegerField(verbose_name='Modbus адрес', )
    department = models.CharField(verbose_name='№ цеха')
    number_of_display = models.IntegerField(verbose_name='Порядок отображения', )
    cable_number = models.IntegerField(verbose_name='№ кабеля', )
    cable_connection_number = models.IntegerField(verbose_name='№ подключения в кабеле', )
    k = models.FloatField(verbose_name='Коэффициент', )
    created_dt = models.DateTimeField(verbose_name='Дата создания', blank=True, null=True)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lines'
        verbose_name = 'Линия'
        verbose_name_plural = 'Линии'

    def __str__(self):
        return f'{self.line_number} - {self.name} - {self.pseudonym}'

    def get_absolute_url(self):
        return reverse('line', kwargs={'line_number': self.line_number})


class LinesCurrentParams(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    line_number = models.IntegerField(verbose_name='№ линии', blank=True, null=True, unique=True)
    connection_counter = models.BooleanField(verbose_name='Наличие связи', blank=True, null=True)
    indicator_value = models.IntegerField(verbose_name='Значение индикатора', blank=True, null=True)
    length = models.FloatField(verbose_name='Метраж, м', blank=True, null=True)
    speed_line = models.FloatField(verbose_name='Скорость линии, м/мин', blank=True, null=True)
    updated_dt = models.DateTimeField(verbose_name='Время обновления', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lines_current_params'
        verbose_name = 'Текущий параметр'
        verbose_name_plural = 'Текущие параметры'

    def __str__(self):
        return f'{self.line_number}'
