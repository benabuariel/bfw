import json
import datetime
import math


def get_capital(state):
    """Function which return capital name of a state, if not found returns None"""
    with open('database/country_capital.json') as json_file:
        data = json.load(json_file)
        for line in data:
            if state.lower() == line['country'].lower():
                return line['city']


def rename_country(code):
    """Function which returns country name out of code of the country
    if not found returns the code"""
    with open('database/country_code.json') as json_file:
        data = json.load(json_file)
        for country in data:
            if country['code'] == code:
                return country['name']
    return code


def loc_list_to_human(loc_list):
    """Function which translate API's loc_list to humans"""
    human_loc = []
    for loc in loc_list:
        append_string = ""
        append_order = [0, 3, 2, 1]
        if len(loc[1]) < 3:
            loc[1] = rename_country(loc[1])
        if len(loc[0]) < 2:
            loc[0] = get_capital(loc[1])
        for i in append_order:
            if len(loc[i]) > 0:
                append_string += (loc[i] + " ")
        human_loc.append(append_string)
    return human_loc


def is_valid_date(val):
    dd = val[:2]
    mm = val[3:5]
    yyyy = val[6:10]
    if len(yyyy) < 4:
        return False
    try:
        dd = int(dd)
        mm = int(mm)
        yyyy = int(yyyy)
    except ValueError:
        return False

    today = datetime.date.today()
    if not (0 <= dd <= 31 and 0 <= mm <= 12 and 2000 <= yyyy <= today.year):  # de-morgan
        return False

    return dd, mm, yyyy


def get_julian_datetime(date):
    """
    Convert a datetime object into julian float.
    Args:
        date: datetime-object of date in question

    Returns: float - Julian calculated datetime.
    Raises:
        TypeError : Incorrect parameter type
        ValueError: Date out of range of equation
    """

    # Ensure correct format
    if not isinstance(date, datetime.datetime):
        raise TypeError('Invalid type for parameter "date" - expecting datetime')
    elif date.year < 1801 or date.year > 2099:
        raise ValueError('Datetime must be between year 1801 and 2099')

    # Perform the calculation
    julian_datetime = 367 * date.year - int((7 * (date.year + int((date.month + 9) / 12.0))) / 4.0) + int(
        (275 * date.month) / 9.0) + date.day + 1721013.5 + (
                              date.hour + date.minute / 60.0 + date.second / math.pow(60,
                                                                                      2)) / 24.0 - 0.5 * math.copysign(
        1, 100 * date.year + date.month - 190002.5) + 0.5

    return julian_datetime


def get_julian_range(year, month, day):
    jul_date = get_julian_datetime(datetime.datetime(year, month, day))
    return jul_date, jul_date + 1


def sql_to_humans(query):
    humidty = {}
    max_temp = {}
    min_temp = {}
    for i, j in zip(range(3, len(query), 3), range(int((len(query)/3)-1))):
        humidty[j] = query[i]
        max_temp[j] = query[i+1]
        min_temp[j] = query[i+2]
    return humidty, max_temp, min_temp


if __name__ == "__main__":
    print(is_valid_date("12/12/2021"))
    print(get_julian_range(2021, 10, 12))

