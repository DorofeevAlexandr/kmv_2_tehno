import datetime as dt
from dotenv import load_dotenv
import os

from django.shortcuts import get_object_or_404
from calendar import month, Month
from os import times
from dateutil.relativedelta import relativedelta
import operator
from .models import Counters, Lines, LinesStatistics


COUNT_LINES = 80


load_dotenv()

VAPOR_GENERATOR_LINES = [75, 76] if os.environ.get('PLACE', 'CVT') == 'CVT' else []


def get_lines_from_base():
    out_lines = []
    lines = Lines.objects.order_by('department')
    for l in lines:
        out_lines.append({'line_number': l.line_number,
                            'name': l.name,
                            'pseudonym': l.pseudonym ,
                            'port': l.port,
                            'department': l.department,
                            'number_of_display': l.number_of_display,
                          })
    return  out_lines

def get_counters_values_from_base(date: dt.date):
    dtime_8_hours = dt.timedelta(hours=8)
    dtime_1_days = dt.timedelta(days=1)
    time_start = dt.datetime(year=date.year,
                             month=date.month,
                             day=date.day,
                             hour=0,
                             minute=0,
                             second=0) + dtime_8_hours
    time_end = time_start + dtime_1_days
    counters = Counters.objects.filter(time__range=[time_start, time_end]).order_by('-time')

    length_in_minute = [[] for _ in range(1441)]

    for c in counters:
        minutes = (c.time - time_start).seconds // 60
        length_in_minute[minutes] = c.lengths
    return  length_in_minute


def get_counters_conections_from_base(date: dt.date):
    dtime_8_hours = dt.timedelta(hours=8)
    dtime_1_days = dt.timedelta(days=1)
    time_start = dt.datetime(year=date.year,
                             month=date.month,
                             day=date.day,
                             hour=0,
                             minute=0,
                             second=0) + dtime_8_hours
    time_end = time_start + dtime_1_days
    conections = Counters.objects.filter(time__range=[time_start, time_end]).order_by('-time')

    conections_in_minute = [[] for _ in range(1441)]

    for c in conections:
        minutes = (c.time - time_start).seconds // 60
        conections_in_minute[minutes] = c.connection_counters
    return  visualization_connections(transposition_conections(conections_in_minute))


def transposition_conections(conections_in_minute):
    transp_conections = [[0 for t in range(1441)] for l in range(COUNT_LINES)]

    for n_minute in range(1, 1441):
        conection_lines = conections_in_minute[n_minute]
        for n_line, conection in enumerate(conection_lines):
            try:
                if conections_in_minute[n_minute][n_line]:
                    transp_conections[n_line][n_minute] = 1
                else:
                    transp_conections[n_line][n_minute] = 0
            except:
                transp_conections[n_line][n_minute] = 0

    return transp_conections


def visualization_connections(transp_conections):
    vis_conections = [[0 for t in range(1441)] for l in range(COUNT_LINES)]
    for n_line in range(COUNT_LINES):
        if transp_conections[n_line][0]:
            chart_value = 100
        else:
            chart_value = 0
        for n_minute in range(1, 1441):
            try:
                if transp_conections[n_line][n_minute]:
                    chart_value += 25
                    chart_value = min(100, chart_value)
                else:
                    chart_value -= 25
                    chart_value = max(0, chart_value)
                vis_conections[n_line][n_minute] = chart_value
            except:
                vis_conections[n_line][n_minute] = chart_value

    return vis_conections


def clear_zero_values(l_values: list):
    last_value = l_values[0]
    for n in range(len(l_values)):
        cur_value = l_values[n]
        if cur_value == 0:
            l_values[n] = last_value
        else:
            last_value = cur_value


def get_transposition_length_in_minute(length_in_minute):
    lengths_lines = [[0 for _ in range(1441)] for _ in range(COUNT_LINES)]
    # Транспонирование матрицы с даными
    for n_minute in range(0, 1441):
        for n_line in range(len(length_in_minute[n_minute])):
            try:
                lengths_lines[n_line][n_minute] = length_in_minute[n_minute][n_line]
            except:
                lengths_lines[n_line][n_minute] = 0
    return lengths_lines


def get_speed_lines(length_in_minute):

    lengths_lines = get_transposition_length_in_minute(length_in_minute)

    for n_line in range(len(lengths_lines)):
        clear_zero_values(lengths_lines[n_line])

    speed_lines = [[0 for _ in range(1441)] for _ in range(COUNT_LINES)]
    for n_line in range(len(lengths_lines)):
        for n_minute in range(1, 1441):
            try:
                speed = (lengths_lines[n_line][n_minute] -
                        lengths_lines[n_line][n_minute - 1]) / 1000
                if speed > 10000 or speed < 0:
                    speed_lines[n_line][n_minute] = 0
                else:
                    speed_lines[n_line][n_minute] = speed
            except:
                speed_lines[n_line][n_minute] = 0
    return speed_lines


def num_smena(minute):
    hour = minute // 60
    if 0 <= hour < 12:
        return 1
    else:
        return 2


def antialiasing_speed_value_3_minute(speed_lines: list):
    for num_lines in range(len(speed_lines)):
        speed0 = speed_lines[num_lines][0]
        speed1 = speed_lines[num_lines][1]
        speed2 = speed_lines[num_lines][2]
        average_speed = (speed0 + speed1 + speed2) / 3
        speed_lines[num_lines][0] = average_speed
        speed_lines[num_lines][1] = average_speed
        for minute in range(len(speed_lines[num_lines])):
            speed2 = speed_lines[num_lines][minute]
            average_speed = (speed0 + speed1 + speed2) / 3
            speed_lines[num_lines][minute] = average_speed
            speed0 = speed1
            speed1 = speed2


def antialiasing_speed_value_5_minute(speed_lines: list):
    for num_lines in range(len(speed_lines)):
        speed0 = speed_lines[num_lines][0]
        speed1 = speed_lines[num_lines][1]
        speed2 = speed_lines[num_lines][2]
        speed3 = speed_lines[num_lines][3]
        speed4 = speed_lines[num_lines][4]
        average_speed = (speed0 + speed1 + speed2 + speed3 + speed4) / 5
        speed_lines[num_lines][0] = average_speed
        speed_lines[num_lines][1] = average_speed
        speed_lines[num_lines][2] = average_speed
        speed_lines[num_lines][3] = average_speed
        for minute in range(len(speed_lines[num_lines])):
            speed4 = speed_lines[num_lines][minute]
            average_speed = (speed0 + speed1 + speed2 + speed3 + speed4) / 5
            speed_lines[num_lines][minute] = average_speed
            speed0 = speed1
            speed1 = speed2
            speed2 = speed3
            speed3 = speed4


def antialiasing_speed_value_10_minute(speed_lines: list, non_antialiasing_lines: list):
    for num_lines in range(len(speed_lines)):
        if num_lines in non_antialiasing_lines:
            for minute in range(len(speed_lines[num_lines])):
                speed = speed_lines[num_lines][minute]
                speed = max(speed, 0)
                speed = min(speed, 110)
                speed_lines[num_lines][minute] = speed
            continue
        speed0 = speed_lines[num_lines][0]
        speed1 = speed_lines[num_lines][1]
        speed2 = speed_lines[num_lines][2]
        speed3 = speed_lines[num_lines][3]
        speed4 = speed_lines[num_lines][4]
        speed5 = speed_lines[num_lines][5]
        speed6 = speed_lines[num_lines][6]
        speed7 = speed_lines[num_lines][7]
        speed8 = speed_lines[num_lines][8]
        speed9 = speed_lines[num_lines][9]

        average_speed = (speed0 + speed1 + speed2 + speed3 + speed4 +
                         speed5 + speed6 + speed7 + speed8 + speed9) / 10
        speed_lines[num_lines][0] = average_speed
        speed_lines[num_lines][1] = average_speed
        speed_lines[num_lines][2] = average_speed
        speed_lines[num_lines][3] = average_speed
        speed_lines[num_lines][4] = average_speed
        speed_lines[num_lines][5] = average_speed
        speed_lines[num_lines][6] = average_speed
        speed_lines[num_lines][7] = average_speed
        speed_lines[num_lines][8] = average_speed
        for minute in range(len(speed_lines[num_lines])):
            speed9 = speed_lines[num_lines][minute]
            average_speed = (speed0 + speed1 + speed2 + speed3 + speed4 +
                             speed5 + speed6 + speed7 + speed8 + speed9) / 10
            speed_lines[num_lines][minute] = average_speed
            speed0 = speed1
            speed1 = speed2
            speed2 = speed3
            speed3 = speed4
            speed4 = speed5
            speed5 = speed6
            speed6 = speed7
            speed7 = speed8
            speed8 = speed9


def fill_zero_spaces(speed_lines, line_number):
    prev_value = 0
    zero_counter = 0
    for minute, value in enumerate(speed_lines[line_number]):
        if value == 0:
            zero_counter += 1
            if zero_counter <=7:
                speed_lines[line_number][minute] = prev_value
        else:
            zero_counter = 0
            prev_value = value


def antialiasing_speed_value(speed_lines: list):
    non_antialiasing_lines = []
    if os.environ.get('PLACE', 'CVT') == 'CVT':
        non_antialiasing_lines = [57 - 1, 75 - 1 , 76 - 1]
    antialiasing_speed_value_10_minute(speed_lines, non_antialiasing_lines)
    for line_index in non_antialiasing_lines:
        fill_zero_spaces(speed_lines, line_index)

def get_str_time(minutes: int):
    hour = minutes // 60
    minute = minutes % 60
    return dt.time(hour=hour, minute=minute).strftime('%H:%M')


def str_average_speed(made_kabel: float, minutes: int):
    if minutes == 0:
        average_speed = 0
    else:
        average_speed = made_kabel / minutes

    return f"{average_speed:6.1f}"


def get_lines_statistic(speed_lines):
    lines_statistic = []

    for num_line in range(COUNT_LINES):
        line_runing = False
        line_statistic = {
            'count_minute_line_run': 0,
            'count_minute_line_run_1': 0,
            'count_minute_line_run_2': 0,

            'max_value': 0,
            'max_value_1': 0,
            'max_value_2': 0,

            'made_kabel': 0,
            'made_kabel_1': 0,
            'made_kabel_2': 0,

            'stop_count': 0,
            'stop_count_1': 0,
            'stop_count_2': 0,
        }

        for minute in range(1438):
            metr_in_minute = speed_lines[num_line][minute]
            metr_in_minute = float(metr_in_minute)
            smena = num_smena(minute)

            if metr_in_minute > 0.2:
                line_runing = True
                line_statistic['count_minute_line_run'] += 1
                if smena == 1:
                    line_statistic['count_minute_line_run_1'] += 1
                if smena == 2:
                    line_statistic['count_minute_line_run_2'] += + 1
            else:
                if line_runing:
                    line_statistic['stop_count'] += 1
                    if smena == 1:
                        line_statistic['stop_count_1'] += 1
                    if smena == 2:
                        line_statistic['stop_count_2'] += 1
                    line_runing = False


            line_statistic['max_value'] = max(line_statistic['max_value'], metr_in_minute)
            if smena == 1:
                line_statistic['max_value_1'] = max(line_statistic['max_value_1'], metr_in_minute)
            if smena == 2:
                line_statistic['max_value_2'] = max(line_statistic['max_value_2'], metr_in_minute)

            line_statistic['made_kabel'] += metr_in_minute
            if smena == 1:
                line_statistic['made_kabel_1'] += metr_in_minute
            if smena == 2:
                line_statistic['made_kabel_2'] += metr_in_minute

        line_statistic['kmv'] = f"{(line_statistic['count_minute_line_run'] / 1440 * 100.0) :6.1f}"
        line_statistic['kmv_1'] = f"{(line_statistic['count_minute_line_run_1'] / 720 * 100.0) :6.1f}"
        line_statistic['kmv_2'] = f"{(line_statistic['count_minute_line_run_2'] / 720 * 100.0) :6.1f}"

        line_statistic['average_speed'] = str_average_speed(line_statistic['made_kabel'], line_statistic['count_minute_line_run'])
        line_statistic['average_speed_1'] = str_average_speed(line_statistic['made_kabel_1'], line_statistic['count_minute_line_run_1'])
        line_statistic['average_speed_2'] = str_average_speed(line_statistic['made_kabel_2'], line_statistic['count_minute_line_run_2'])

        line_statistic['made_kabel'] = line_statistic['made_kabel'] / 1000
        line_statistic['made_kabel_1'] = line_statistic['made_kabel_1'] / 1000
        line_statistic['made_kabel_2'] = line_statistic['made_kabel_2'] / 1000

        line_statistic['count_minute_line_run'] = get_str_time(line_statistic['count_minute_line_run'])
        line_statistic['count_minute_line_run_1'] = get_str_time(line_statistic['count_minute_line_run_1'])
        line_statistic['count_minute_line_run_2'] = get_str_time(line_statistic['count_minute_line_run_2'])

        line_statistic['max_value'] = f"{line_statistic['max_value']:6.1f}"
        line_statistic['max_value_1'] = f"{line_statistic['max_value_1']:6.1f}"
        line_statistic['max_value_2'] = f"{line_statistic['max_value_2']:6.1f}"

        line_statistic['made_kabel'] = f"{line_statistic['made_kabel']:6.1f}"
        line_statistic['made_kabel_1'] = f"{line_statistic['made_kabel_1']:6.1f}"
        line_statistic['made_kabel_2'] = f"{line_statistic['made_kabel_2']:6.1f}"

        line_statistic['label_count_minute_line_run'] = 'Время работы'
        line_statistic['label_max_value'] = 'Макс. скорость, м/мин	'
        line_statistic['label_average_speed'] = 'Средн. скорость, м/мин	'
        line_statistic['label_made_kabel'] = 'Изготовленно, км'
        line_statistic['label_stop_count'] = 'Количество остановок'
        line_statistic['label_kmv'] = 'КМВ'


        lines_statistic.append(line_statistic)

    return lines_statistic


def change_line_stat_twists_in_minute(lines_statistic: list, n: int):
    lines_statistic[n - 1]['label_max_value'] = 'Макс. скорость, скруток/мин'
    lines_statistic[n - 1]['label_average_speed'] = 'Средн. скорость, скруток/мин'
    lines_statistic[n - 1]['label_made_kabel'] = 'Изготовленно, тыс. скруток'


def change_line_stat_kg_in_minute(lines_statistic: list, n: int):
    lines_statistic[n - 1]['label_max_value'] = 'Макс. скорость, кг/мин'
    lines_statistic[n - 1]['label_average_speed'] = 'Средн. скорость, кг/мин'
    lines_statistic[n - 1]['label_made_kabel'] = 'Изготовленно, т.'


def change_line_stat_metr_in_second(lines_statistic: list, n: int):
    lines_statistic[n - 1]['label_max_value'] = 'Макс. скорость, м/с'
    lines_statistic[n - 1]['label_average_speed'] = 'Средн. скорость, м/с'

    lines_statistic[n - 1]['max_value'] = f"{(float(lines_statistic[n - 1]['max_value']) / 60.0):5.1f}"
    lines_statistic[n - 1]['max_value_1'] = f"{(float(lines_statistic[n - 1]['max_value_1']) / 60.0):5.1f}"
    lines_statistic[n - 1]['max_value_2'] = f"{(float(lines_statistic[n - 1]['max_value_2']) / 60.0):5.1f}"

    lines_statistic[n - 1]['average_speed'] = f"{(float(lines_statistic[n - 1]['average_speed']) / 60.0):5.1f}"
    lines_statistic[n - 1]['average_speed_1'] = f"{(float(lines_statistic[n - 1]['average_speed_1']) / 60.0):5.1f}"
    lines_statistic[n - 1]['average_speed_2'] = f"{(float(lines_statistic[n - 1]['average_speed_2']) / 60.0):5.1f}"


def change_line_stat_clear_data(lines_statistic: list, n: int):
    lines_statistic[n - 1]['label_max_value'] = ' '
    lines_statistic[n - 1]['label_average_speed'] = ' '
    lines_statistic[n - 1]['label_made_kabel'] = ' '

    lines_statistic[n - 1]['max_value'] = ''
    lines_statistic[n - 1]['max_value_1'] = ''
    lines_statistic[n - 1]['max_value_2'] = ''

    lines_statistic[n - 1]['average_speed'] = ''
    lines_statistic[n - 1]['average_speed_1'] = ''
    lines_statistic[n - 1]['average_speed_2'] = ''

    lines_statistic[n - 1]['made_kabel'] = ''
    lines_statistic[n - 1]['made_kabel_1'] = ''
    lines_statistic[n - 1]['made_kabel_2'] = ''


def change_title_lines_statistic(lines_statistic:list):
    change_line_stat_twists_in_minute(lines_statistic, 6)
    change_line_stat_twists_in_minute(lines_statistic, 7)

    change_line_stat_metr_in_second(lines_statistic, 9)
    change_line_stat_metr_in_second(lines_statistic, 23)

    change_line_stat_kg_in_minute(lines_statistic, 46)
    change_line_stat_kg_in_minute(lines_statistic, 47)
    change_line_stat_kg_in_minute(lines_statistic, 48)
    change_line_stat_kg_in_minute(lines_statistic, 49)

    change_line_stat_twists_in_minute(lines_statistic, 50)

    change_line_stat_clear_data(lines_statistic, 57)
    change_line_stat_clear_data(lines_statistic, 75)
    change_line_stat_clear_data(lines_statistic, 76)


def change_speed_lines_metr_in_second(speed_lines:list, num_lines: int):
    for minute in range(0, len(speed_lines[num_lines -1])):
        speed_lines[num_lines -1][minute] = speed_lines[num_lines -1][minute] / 60.0

def change_speed_lines(speed_lines:list):
    change_speed_lines_metr_in_second(speed_lines, 9)
    change_speed_lines_metr_in_second(speed_lines, 23)


def get_smale_speed_lines(speed_lines: list, step=5):
    result = []
    for num_lines in range(len(speed_lines)):
        result.append([])
        for minute in range(0, len(speed_lines[num_lines]), step):
            result[num_lines].append(speed_lines[num_lines][minute])
    return result


def get_departments(lines: list):
    department_1 = sorted(filter(lambda line: line['department'] == '1', lines), key=lambda l: l["number_of_display"])
    department_2 = sorted(filter(lambda line: line['department'] == '2', lines), key=lambda l: l["number_of_display"])
    department_3 = sorted(filter(lambda line: line['department'] == '3', lines), key=lambda l: l["number_of_display"])
    # department_4 = sorted(filter(lambda line: line['department'] == 'ППК', lines), key=lambda l: l["number_of_display"])
    return [
            department_1,
            department_2,
            department_3,
            # department_4
           ]


def get_departments_ppk(lines: list):
    department_4 = sorted(filter(lambda line: line['department'] == 'ППК', lines), key=lambda l: l["number_of_display"])
    return [
            department_4
           ]


def get_data_in_select_date(select_date: dt.datetime):
    counters_values = get_counters_values_from_base(select_date)
    # print(counters_values)
    speed_lines = get_speed_lines(counters_values)
    antialiasing_speed_value(speed_lines)
    # print(speed_lines)

    lines_statistic = get_lines_statistic(speed_lines)

    if os.environ.get('PLACE', 'CVT') == 'CVT':
        change_title_lines_statistic(lines_statistic)
    step = 3
    smale_speed_lines = get_smale_speed_lines(speed_lines, step)
    change_speed_lines(smale_speed_lines)
    time = [dt.time(hour=(((n * step) // 60) + 8) % 24, minute=((n * step) % 60)) for n, speed in
            enumerate(smale_speed_lines[0])]
    return time, smale_speed_lines, lines_statistic


def fill_zero_spaces_by_key(speed_lines, key):
    prev_value = 0
    zero_counter = 0
    for values in speed_lines:
        value = values[key]
        if value == 0:
            zero_counter += 1
            if zero_counter <= 2:
                values[key] = prev_value
        else:
            zero_counter = 0
            prev_value = value


def decode_vapor_generator_trend(speed_lines, line_number):
    values = []
    for speed in speed_lines[line_number - 1]:
        sp = int(speed)
        # print(line_number, speed, sp)
        heating = 25 if sp == 10 or sp == 110 else 0
        temperature = 100 if sp == 100 or sp == 110 or sp == 101 else 0
        values.append({'heating' : heating,
                       'temperature' : temperature,
                       'sp' : sp})
    return values


def get_sorted_departments_data(departments, lines_statistic, smale_speed_lines):
    out_department = []
    for department in departments:
        out_lines = []
        for line in department:
            n = line['line_number']
            if lines_statistic and smale_speed_lines:
                if n in VAPOR_GENERATOR_LINES:
                    # print(n)
                    speed = decode_vapor_generator_trend(speed_lines=smale_speed_lines,
                                                         line_number=n)
                    fill_zero_spaces_by_key(speed,
                                     key='heating' )
                    fill_zero_spaces_by_key(speed,
                                     key='temperature')
                else:
                    speed = [int(sp) for sp in  smale_speed_lines[n - 1]]
                out_lines.append({**line,
                                  'statistic': lines_statistic[n - 1],
                                  'speed': speed} )
        out_department.append(out_lines)
    return out_department


def get_lines_statistic_for_date(date: dt.date):
    counters_values = get_counters_values_from_base(date)
    speed_lines = get_speed_lines(counters_values)
    antialiasing_speed_value(speed_lines)
    return get_lines_statistic(speed_lines)


def get_statistics_select_period(start_date: dt.date, step_months=1):
    end_date = start_date + relativedelta(months = step_months)

    made_kabel_in_days = []
    times = []

    if start_date:
        cur_date = start_date
        made_kabel_in_days = []
        times = []
        while cur_date < end_date:
            # print(cur_date)
            made_kabel_in_days.append([int(float(ls['made_kabel']) * 1000) for ls in get_lines_statistic_for_date(cur_date)])
            times.append(cur_date)

            cur_date = cur_date + dt.timedelta(days=1)
        # print(made_kabel_in_days)
    return times, made_kabel_in_days


def save_made_kabel_in_base(cur_date: dt.date, made_kabel: list):
    m_k = LinesStatistics()
    m_k.date = cur_date
    m_k.made_kabel = '{' + ', '.join(map(str, made_kabel)) + '}'
    m_k.save()


def create_zero_values_counters():
    return  [0 for _ in range(COUNT_LINES)]


def get_made_kabel_in_cur_month(cur_date: dt.date):
    t, made_kabel_in_days = get_statistics_select_period_and_wr_base(cur_date, step_months=1)
    made_kabel_in_cur_month = create_zero_values_counters()
    for made_kabel_in_day in made_kabel_in_days:
        made_kabel_in_cur_month = list(map(operator.add, made_kabel_in_cur_month, made_kabel_in_day))
    # print(made_kabel_in_cur_month)
    return made_kabel_in_cur_month


def get_statistics_select_period_and_wr_base(start_date: dt.date, step_months=1):
    end_date = start_date + relativedelta(months = step_months)
    made_kabel_in_days = []
    times = []
    if start_date:
        cur_date = start_date
        made_kabel_in_days = []
        times = []
        while cur_date < end_date:
            if cur_date < dt.date.today():
                if LinesStatistics.objects.filter(date=cur_date).order_by('-date').exists():
                    m_k = get_object_or_404(LinesStatistics, date=cur_date)
                    made_kabel = m_k.made_kabel
                else:
                    made_kabel = [int(float(ls['made_kabel']) * 1000) for ls in get_lines_statistic_for_date(cur_date)]
                    save_made_kabel_in_base(cur_date, made_kabel)
            elif cur_date == dt.date.today():
                made_kabel = [int(float(ls['made_kabel']) * 1000) for ls in get_lines_statistic_for_date(cur_date)]
            else:
                made_kabel = create_zero_values_counters()
            made_kabel_in_days.append(made_kabel)
            times.append(cur_date)

            cur_date = cur_date + dt.timedelta(days=1)
        # print(made_kabel_in_days)
    return times, made_kabel_in_days


def get_sorted_departments_statistic(departments, made_kabel_in_days):
    out_department = []
    for department in departments:
        out_lines = []
        for line in department:
            n = line['line_number']
            if made_kabel_in_days:
                made_kabel = [day_values[n - 1] for day_values in  made_kabel_in_days]
                sum_made_kabel = sum(made_kabel) / 1000
                made_kabel = [int(value / 1000) for value in made_kabel]
                out_lines.append({**line,
                                  'sum_made_kabel': sum_made_kabel,
                                  'made_kabel': made_kabel} )
        out_department.append(out_lines)
    return out_department
