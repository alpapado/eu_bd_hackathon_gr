import numpy as np
import pandas as pd
import time
import utils

data_root = "../datasets/covid-19-main"
covid_data_file = data_root + "/data/countries-aggregated.csv"
countries_data_file = data_root + "/data/reference.csv"
covid_df = pd.read_csv(covid_data_file, parse_dates=["Date"])
countries_df = pd.read_csv(countries_data_file)


def get_covid_data_for_country_for_period(country_code, time_period):
    """
    country_code: iso2 code
    time_period: Either YearMonth string or Year string

    """
    country = countries_df[countries_df["iso2"] == country_code]["Combined_Key"].iloc[0]

    if len(time_period) == 4:
        # Time period is year
        year = int(time_period)
        period_entries = covid_df[
            (covid_df["Country"] == country) & (covid_df["Date"].dt.year == year)
        ]
    elif len(time_period) == 6:
        # Time period is yearMonth
        year = int(time_period[:4])
        month = int(time_period[4:])
        period_entries = covid_df[
            (covid_df["Country"] == country)
            & (covid_df["Date"].dt.year == year)
            & (covid_df["Date"].dt.month == month)
        ]

    return period_entries


def get_covid_stats_for_previous_year(country_code, time_period):
    period_end = time_period
    period_start = time_period
    new_cases = []
    deaths = []
    active_cases = []

    for i in range(12):
        period_start = utils.get_previous_period(period_start)

    this_period = period_start
    for i in range(13):
        stats = get_covid_summary_for_country_for_period(country_code, this_period)
        this_period = utils.get_next_period(this_period)
        new_cases.append(stats["new_cases"])
        deaths.append(stats["deaths"])
        active_cases.append(stats["active_cases"])

    return new_cases, deaths, active_cases


def get_covid_summary_for_country_for_period(country_code, time_period):
    previous_period = get_previous_period(time_period)
    per_day_prev_period = get_covid_data_for_country_for_period(
        country_code, previous_period
    )
    per_day = get_covid_data_for_country_for_period(country_code, time_period)
    this_period_stats = summarize_df(per_day)
    prev_period_stats = summarize_df(per_day_prev_period)

    period_stats = this_period_stats
    period_stats["diff_active_cases"] = np.nan_to_num(
        np.round(
            100.0
            * (
                (period_stats["active_cases"] - prev_period_stats["active_cases"])
                / prev_period_stats["active_cases"]
            ),
            2,
        ), posinf=np.inf,
    )
    return period_stats


def summarize_df(df):
    new_cases = df["Confirmed"].diff().sum()
    deaths = df["Deaths"].diff().sum()
    active_cases = (df["Confirmed"] - df["Recovered"] - df["Deaths"]).median()
    stats = {
        "new_cases": np.nan_to_num(new_cases),
        "deaths": np.nan_to_num(deaths),
        "active_cases": np.nan_to_num(active_cases),
    }
    return stats


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


def demo():
    # df = get_covid_data_for_country_for_period("GR", "202012")
    #period_stats = get_covid_summary_for_country_for_period("GR", "202008")
    get_covid_stats_for_previous_year("GR", "202008")
    bb = 1


if __name__ == "__main__":
    demo()
