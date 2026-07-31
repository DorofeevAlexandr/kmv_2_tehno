from django.urls import path, re_path, register_converter
from . import views
from . import converters


register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path('', views.index, name='home'),
    path('statistic', views.statistic, name='statistic'),
    path('statistics_for_the_year', views.statistics_for_the_year, name='statistics_for_the_year'),
    path('ppk', views.data_in_day_ppk, name='data_in_day_ppk'),
    path('statistic_ppk', views.statistic_ppk, name='statistic_ppk'),
    path('statistics_for_the_year_ppk', views.statistics_for_the_year_ppk, name='statistics_for_the_year_ppk'),
    path('tuning', views.tuning, name='tuning'),
    path('line/<int:line_number>/', views.update_line, name='line'),
    path('connection_with_counters', views.connection_with_counters, name='connection_with_counters'),
]
