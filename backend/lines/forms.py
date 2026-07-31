import datetime as dt
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.deconstruct import deconstructible
from django.db import models


class ReadDataCounters(forms.Form):
    day = forms.DateField(initial=dt.date.today,
                          label="Выберите дату",
                          required=True,
                          widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
                          input_formats=["%Y-%m-%d"]
                          )


class ReadAndSaveLinesStatistic(forms.Form):
    start_day = forms.DateField(initial=dt.date.today,
                          label="Выберите месяц",
                          required=True,
                          widget=forms.DateInput(format="%Y-%m", attrs={"type": "month"}),
                          input_formats=["%Y-%m"]
                          )
    show_tables = forms.BooleanField(initial=True,
                                label="Показать таблицы",
                                required=False
                                )
    show_charts = forms.BooleanField(initial=True,
                                label="Показать графики",
                                required=False
                                )


class SelectYearLinesStatistic(forms.Form):
    select_year = forms.IntegerField(initial=dt.date.today().year,
                          label="Выберите год",
                          required=True,
                          max_value = dt.date.today().year,
                          min_value = 2024,
                          step_size = 1,
                          )
    show_tables = forms.BooleanField(initial=True,
                                label="Показать таблицы",
                                required=False
                                )
    show_charts = forms.BooleanField(initial=True,
                                label="Показать графики",
                                required=False
                                )


class LineParamsKUpdateForm(forms.Form):
    k = forms.FloatField(required=True,
                         min_value=0,
                         step_size=0.000000000000000001,
                         )
