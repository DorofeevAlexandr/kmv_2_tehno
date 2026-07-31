from django.contrib import admin
from .models import Counters, LinesStatistics, Lines, LinesCurrentParams


admin.site.site_header = "Панель администрирования"
admin.site.index_title = "Контроль машинного времени"


@admin.register(Counters)
class CountersAdmin(admin.ModelAdmin):
    # Отображение полей в списке
    list_display = ('time', 'lengths', 'connection_counters', )
    # Фильтрация в списке
    list_filter = ('time',)
    # Поиск по полям
    search_fields = ('time',)
    date_hierarchy = 'time'


@admin.register(LinesStatistics)
class LinesStatisticsAdmin(admin.ModelAdmin):
    # Отображение полей в списке
    list_display = ('date', 'made_kabel', )
    # Фильтрация в списке
    list_filter = ('date',)
    # Поиск по полям
    search_fields = ('date',)
    date_hierarchy = 'date'


@admin.register(Lines)
class LinesAdmin(admin.ModelAdmin):
    # Отображение полей в списке
    list_display = ('line_number', 'name', 'pseudonym',
                    'port', 'modbus_adr',
                    'department', 'number_of_display',
                    'k', 'created_dt', 'description',)
    # Фильтрация в списке
    list_filter = ('port', 'department',)
    # Поиск по полям
    search_fields = ('line_number', 'pseudonym',)
    list_editable = ('number_of_display', )


@admin.register(LinesCurrentParams)
class LinesCurrentParamsAdmin(admin.ModelAdmin):
    # Отображение полей в списке
    list_display = ('line_number', 'connection_counter', 'indicator_value', 'length', 'speed_line', 'updated_dt', )
    # Фильтрация в списке
    # list_filter = ('line_number',)
    # Поиск по полям
    search_fields = ('line_number',)
