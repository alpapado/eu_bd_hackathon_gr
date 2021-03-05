import math
import numpy as np
import pandas as pd
import time

country_codes = pd.read_csv("../datasets/countries_all.csv", keep_default_na=False)
country_coords = pd.read_csv("../datasets/country_coords.csv", keep_default_na=False)
with open('countries_eu.txt') as f:
    content = f.readlines()
eu_codes = [x.strip() for x in content]


def get_country_name_from_iso_code(country_code):
    try:
        name = country_codes[country_codes["Code"]
                             == country_code]['Name'].iat[0]
    except IndexError:
        name = "Unknown"
    return name


def is_country_in_europe(country_code):
    result = country_code in eu_codes
    return result


def spherical2mercator(lat, lon, map_width, map_height):
    x = (lon + 180) * (map_width / 360)
    lat_rad = lat * np.pi / 180
    merc_n = np.log(np.tan((np.pi / 4) + (lat_rad / 2)))
    y = (map_height / 2) - (map_width * merc_n / (2 * np.pi))
    return x, y


def country_code_to_x_y(country_code, map_width=500, map_height=500):
    lat = country_coords[country_coords["Code"]
                         == country_code]["Latitude"].iat[0]
    lon = country_coords[country_coords["Code"]
                         == country_code]["Longitude"].iat[0]

    return spherical2mercator(lat, lon, map_width, map_height)


def check_if_eu_selected_multi(multidata):
    for x in multidata:
        if x['id'] == 'eu':
            return True
    return False


def check_if_eu_selected_single(data):
    if data['id'] == 'eu':
        return True
    else:
        return False


def convert_date_to_str(this_date):
    splits = str(this_date).split('-')
    return splits[0]+splits[1]

def get_previous_period(time_period):
    year_int = int(time_period[:4])
    month_int = int(time_period[4:])
    prev_month_int = month_int - 1
    if prev_month_int == 0:
        prev_month_int = 12
        year_int -= 1

    if prev_month_int >= 10:
        prev_period = str(year_int) + str(prev_month_int)
    else:
        prev_period = str(year_int) + "0" + str(prev_month_int)

    return prev_period

def get_next_period(time_period):
    year_int = int(time_period[:4])
    month_int = int(time_period[4:])
    next_month_int = month_int + 1
    if next_month_int == 13:
        next_month_int = 1
        year_int += 1

    if next_month_int >= 10:
        next_period = str(year_int) + str(next_month_int)
    else:
        next_period = str(year_int) + "0" + str(next_month_int)

    return next_period


if __name__ == "__main__":
    print(get_country_name_from_iso_code("NA"))
    print(is_country_in_europe("AE"))
