import datetime as dt
from dateutil.relativedelta import relativedelta
import locale


from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.template.loader import render_to_string
from .forms import (ReadDataCounters, ReadAndSaveLinesStatistic, SelectYearLinesStatistic, LineParamsKUpdateForm)
from .work_with_data import (get_data_in_select_date, get_departments, get_departments_ppk,
                             get_lines_from_base, get_sorted_departments_data, get_sorted_departments_statistic,
                             get_statistics_select_period, get_statistics_select_period_and_wr_base,
                             get_made_kabel_in_cur_month, get_counters_conections_from_base)
from .models import Lines, LinesCurrentParams

menu = [{'title': "Данные за день", 'url_name': 'home'},
        {'title': "Статистика за месяц", 'url_name': 'statistic'},
        {'title': "Статистика за год", 'url_name': 'statistics_for_the_year'},
        {'title': "", 'url_name': 'tuning'},
]

menu_ppk = [{'title': "Данные за день ППК", 'url_name': 'data_in_day_ppk'},
        {'title': "Статистика за месяц ППК", 'url_name': 'statistic_ppk'},
        {'title': "Статистика за год ППК", 'url_name': 'statistics_for_the_year_ppk'},
        {'title': "", 'url_name': 'tuning'},
]

menu_tuning = [{'title': "Данные за день", 'url_name': 'home'},
        {'title': "Статистика за месяц", 'url_name': 'statistic'},
        {'title': "Статистика за год", 'url_name': 'statistics_for_the_year'},
        {'title': "Связь со счетчиками", 'url_name': 'connection_with_counters'},
        {'title': "Настройка", 'url_name': 'tuning'},
]

def index(request):
    smale_speed_lines = []
    lines_statistic = []
    time = []
    lines = get_lines_from_base()
    if request.method == 'POST':
        form = ReadDataCounters(request.POST, request.FILES)
        if form.is_valid():
            select_date = form.cleaned_data.get('day', None)
            if select_date:
                time, smale_speed_lines, lines_statistic = get_data_in_select_date(select_date)
    else:
        form = ReadDataCounters()

    departments = get_departments(lines)
    out_department = get_sorted_departments_data(departments, lines_statistic, smale_speed_lines)

    data = {
        'title': 'КМВ - Данные за день',
        'departments': out_department,
        'form': form,
        'times': time,
        'menu': menu,
    }
    return render(request, 'lines/index.html', context=data)


def data_in_day_ppk(request):
    smale_speed_lines = []
    lines_statistic = []
    time = []
    lines = get_lines_from_base()
    if request.method == 'POST':
        form = ReadDataCounters(request.POST, request.FILES)
        if form.is_valid():
            select_date = form.cleaned_data.get('day', None)
            if select_date:
                time, smale_speed_lines, lines_statistic = get_data_in_select_date(select_date)
    else:
        form = ReadDataCounters()

    departments = get_departments_ppk(lines)
    out_department = get_sorted_departments_data(departments, lines_statistic, smale_speed_lines)

    data = {
        'title': 'КМВ - Данные за день ППК',
        'departments': out_department,
        'form': form,
        'times': time,
        'menu': menu_ppk,
    }
    return render(request, 'lines/index.html', context=data)


def statistic(request):
    made_kabel_in_days = []
    times = []
    lines = get_lines_from_base()
    show_tables = True
    show_charts = True
    if request.method == 'POST':
        form = ReadAndSaveLinesStatistic(request.POST, request.FILES)
        if form.is_valid():
            show_tables = form.cleaned_data.get('show_tables', None)
            show_charts = form.cleaned_data.get('show_charts', None)
            calendar_date = form.cleaned_data.get('start_day', None)
            start_date = dt.date(year=calendar_date.year,
                                 month=calendar_date.month,
                                 day=1)
            times, made_kabel_in_days = get_statistics_select_period_and_wr_base(start_date)
    else:
        form = ReadAndSaveLinesStatistic()

    departments = get_departments(lines)
    out_department = get_sorted_departments_statistic(departments, made_kabel_in_days)

    data = {
        'title': 'КМВ - Статистика за месяц',
        'menu': menu,
        'departments': out_department,
        'form': form,
        'times': times,
        'show_tables': show_tables,
        'show_charts': show_charts,
    }
    return render(request, 'lines/statistic.html', context=data)


def statistic_ppk(request):
    made_kabel_in_days = []
    times = []
    lines = get_lines_from_base()
    show_tables = True
    show_charts = True
    if request.method == 'POST':
        form = ReadAndSaveLinesStatistic(request.POST, request.FILES)
        if form.is_valid():
            show_tables = form.cleaned_data.get('show_tables', None)
            show_charts = form.cleaned_data.get('show_charts', None)
            calendar_date = form.cleaned_data.get('start_day', None)
            start_date = dt.date(year=calendar_date.year,
                                 month=calendar_date.month,
                                 day=1)
            times, made_kabel_in_days = get_statistics_select_period_and_wr_base(start_date)
    else:
        form = ReadAndSaveLinesStatistic()

    departments = get_departments_ppk(lines)
    out_department = get_sorted_departments_statistic(departments, made_kabel_in_days)

    data = {
        'title': 'КМВ - Статистика за месяц ППК',
        'menu': menu_ppk,
        'departments': out_department,
        'form': form,
        'times': times,
        'show_tables': show_tables,
        'show_charts': show_charts,
    }
    return render(request, 'lines/statistic.html', context=data)


def statistics_for_the_year(request):
    made_kabel_in_months = []
    times = []
    lines = get_lines_from_base()
    select_year = dt.date.today().year
    show_tables = True
    show_charts = True
    if request.method == 'POST':
        form = SelectYearLinesStatistic(request.POST, request.FILES)
        if form.is_valid():
            show_tables = form.cleaned_data.get('show_tables', None)
            show_charts = form.cleaned_data.get('show_charts', None)
            select_year = form.cleaned_data.get('select_year', None)
            start_date = dt.date(year=select_year,
                                 month=1,
                                 day=1)
            end_date = start_date + relativedelta(months=12)
            cur_date = start_date
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

            while cur_date < end_date:
                made_kabel_in_cur_month = get_made_kabel_in_cur_month(cur_date)
                made_kabel_in_months.append(made_kabel_in_cur_month)
                times.append(cur_date.strftime("%b %Y"))
                cur_date += relativedelta(months=1)
    else:
        form = SelectYearLinesStatistic()

    departments = get_departments(lines)
    out_department = get_sorted_departments_statistic(departments, made_kabel_in_months)

    data = {
        'title': f'КМВ - Статистика за {str(select_year)} год',
        'menu': menu,
        'departments': out_department,
        'form': form,
        'times': times,
        'show_tables': show_tables,
        'show_charts': show_charts,
    }
    return render(request, 'lines/statistics_for_the_year.html', context=data)


def statistics_for_the_year_ppk(request):
    made_kabel_in_months = []
    times = []
    lines = get_lines_from_base()
    select_year = dt.date.today().year
    show_tables = True
    show_charts = True
    if request.method == 'POST':
        form = SelectYearLinesStatistic(request.POST, request.FILES)
        if form.is_valid():
            show_tables = form.cleaned_data.get('show_tables', None)
            show_charts = form.cleaned_data.get('show_charts', None)
            select_year = form.cleaned_data.get('select_year', None)
            start_date = dt.date(year=select_year,
                                 month=1,
                                 day=1)
            end_date = start_date + relativedelta(months=12)
            cur_date = start_date
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

            while cur_date < end_date:
                made_kabel_in_cur_month = get_made_kabel_in_cur_month(cur_date)
                made_kabel_in_months.append(made_kabel_in_cur_month)
                times.append(cur_date.strftime("%b %Y"))
                cur_date += relativedelta(months=1)
    else:
        form = SelectYearLinesStatistic()

    departments = get_departments_ppk(lines)
    out_department = get_sorted_departments_statistic(departments, made_kabel_in_months)

    data = {
        'title': f'КМВ - Статистика за {str(select_year)} год ППК',
        'menu': menu_ppk,
        'departments': out_department,
        'form': form,
        'times': times,
        'show_tables': show_tables,
        'show_charts': show_charts,
    }
    return render(request, 'lines/statistics_for_the_year.html', context=data)


def get_lines_params_from_base():
    out_lines = []
    lines = Lines.objects.order_by('line_number')
    for line in lines:
        line_number = line.line_number
        line_current_params = get_object_or_404(LinesCurrentParams, line_number=line_number)
        out_lines.append({'line_number': line.line_number,
                            'name': line.name,
                            'modbus_adr': line.modbus_adr,
                            'pseudonym': line.pseudonym ,
                            'port': line.port,
                            'department': line.department,
                            'number_of_display': line.number_of_display,
                            'k': line.k,
                            'indicator_value': line_current_params.indicator_value,
                            'connection_counter': line_current_params.connection_counter,
                            'length': line_current_params.length,
                            'speed_line': line_current_params.speed_line,
                            'line_url': line.get_absolute_url(),
                          })
    return  out_lines


def tuning(request):
    lines = get_lines_params_from_base()
    data = {
        'title': 'КМВ - настройка',
        'menu': menu_tuning,
        'lines': lines,
    }
    return render(request, 'lines/tuning.html', context=data)


def about(request):
    return render(request, 'lines/about.html')


def update_line(request, line_number):
    line = get_object_or_404(Lines, line_number=line_number)
    line_current_params = get_object_or_404(LinesCurrentParams, line_number=line_number)
    if request.method == 'POST':
        form = LineParamsKUpdateForm(request.POST)
        if form.is_valid():
            try:
                # line.objects.create(**form.cleaned_data)
                update_line = Lines.objects.filter(line_number=line_number).get()
                update_line.k = form.cleaned_data['k']
                update_line.save(update_fields=['k'])
                return redirect('tuning')
            except:
                form.add_error(None, "Ошибка обновления параметров линии")
    else:
        form = LineParamsKUpdateForm(initial=model_to_dict(line))
    data = {
        'title': f'КМВ - настройка линии № {int(line_number)}' ,
        'menu': menu_tuning,
        'line': line,
        'line_current_params': line_current_params,
        'form': form,
    }
    return render(request, 'lines/line.html', context=data)


def connection_with_counters(request):
    lines_connections = []
    time = []
    lines0 = get_lines_from_base()
    lines = sorted(lines0, key=lambda d: d['line_number'])
    # print(*lines)
    if request.method == 'POST':
        form = ReadDataCounters(request.POST, request.FILES)
        if form.is_valid():
            select_date = form.cleaned_data.get('day', None)
            if select_date:
                lines_connections = get_counters_conections_from_base(select_date)
                time = [dt.time(hour=((n // 60) + 8) % 24, minute=(n % 60)) for n, connection in
                        enumerate(lines_connections[0])]
    else:
        form = ReadDataCounters()

    for l in lines:
        try:
            l['lines_connections'] = lines_connections[l['line_number']-1]
        except:
            l['lines_connections'] = []

    data = {
        'title': 'КМВ - Связь со счетчиками',
        'lines': lines,
        'form': form,
        'times': time,
        'menu': menu_tuning,
    }
    return render(request, 'lines/lines_connections.html', context=data)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
