import numpy as np
import pandas as pd
import time

import utils
from comext import COMEXTParser


def get_trade_stats_for_country(df, country_code):
    imports = df[(df["PARTNER_ISO"] == country_code) & (df["FLOW"] == 2)]
    exports = df[(df["PARTNER_ISO"] == country_code) & (df["FLOW"] == 1)]

    import_value, import_kg = (
        int(imports["VALUE_IN_EUROS"].sum()),
        int(imports["QUANTITY_IN_KG"].sum()),
    )
    export_value, export_kg = (
        int(exports["VALUE_IN_EUROS"].sum()),
        int(exports["QUANTITY_IN_KG"].sum()),
    )

    trade_stats = {
        "import_value": import_value,
        "import_kg": import_kg,
        "export_value": export_value,
        "export_kg": export_kg,
    }
    return trade_stats


def get_trade_stats_for_country_for_period(df, country_code, period):
    imports = df[
        (df["PERIOD"] == period)
        & (df["PARTNER_ISO"] == country_code)
        & (df["FLOW"] == 2)
    ]
    exports = df[
        (df["PERIOD"] == period)
        & (df["PARTNER_ISO"] == country_code)
        & (df["FLOW"] == 1)
    ]

    import_value, import_kg = (
        int(imports["VALUE_IN_EUROS"].sum()),
        int(imports["QUANTITY_IN_KG"].sum()),
    )
    export_value, export_kg = (
        int(exports["VALUE_IN_EUROS"].sum()),
        int(exports["QUANTITY_IN_KG"].sum()),
    )

    trade_stats = {
        "import_value": import_value,
        "import_kg": import_kg,
        "export_value": export_value,
        "export_kg": export_kg,
    }
    return trade_stats


def get_trade_stats_for_2_countries(df, country_1, country_2):
    imports_1_from_2 = df[
        (df["PARTNER_ISO"] == country_1)
        & (df["DECLARANT_ISO"] == country_2)
        & (df["FLOW"] == 2)
    ]
    exports_1_to_2 = df[
        (df["PARTNER_ISO"] == country_1)
        & (df["DECLARANT_ISO"] == country_2)
        & (df["FLOW"] == 1)
    ]

    imports_2_from_1 = df[
        (df["PARTNER_ISO"] == country_2)
        & (df["DECLARANT_ISO"] == country_1)
        & (df["FLOW"] == 2)
    ]

    exports_2_to_1 = df[
        (df["PARTNER_ISO"] == country_2)
        & (df["DECLARANT_ISO"] == country_1)
        & (df["FLOW"] == 1)
    ]

    import_value, import_kg = (
        int(imports_1_from_2["VALUE_IN_EUROS"].sum()),
        int(imports_1_from_2["QUANTITY_IN_KG"].sum()),
    )
    export_value, export_kg = (
        int(exports_1_to_2["VALUE_IN_EUROS"].sum()),
        int(exports_1_to_2["QUANTITY_IN_KG"].sum()),
    )

    trade_stats_1_2 = {
        "import_value": import_value,
        "import_kg": import_kg,
        "export_value": export_value,
        "export_kg": export_kg,
    }

    import_value, import_kg = (
        int(imports_2_from_1["VALUE_IN_EUROS"].sum()),
        int(imports_2_from_1["QUANTITY_IN_KG"].sum()),
    )
    export_value, export_kg = (
        int(exports_2_to_1["VALUE_IN_EUROS"].sum()),
        int(exports_2_to_1["QUANTITY_IN_KG"].sum()),
    )

    trade_stats_2_1 = {
        "import_value": import_value,
        "import_kg": import_kg,
        "export_value": export_value,
        "export_kg": export_kg,
    }
    return trade_stats_1_2, trade_stats_2_1


def get_trade_stats_for_previous_year(country_code, period, product):
    comext_parser = COMEXTParser()

    period_end = period
    period_start = period
    import_values = []
    export_values = []
    t1 = time.time()

    for i in range(12):
        period_start = utils.get_previous_period(period_start)

    df = comext_parser.get_data_as_df_for_period_range(period_start, period_end, product)

    this_period = period_start
    for i in range(13):
        stats = get_trade_stats_for_country_for_period(df, country_code, this_period)
        this_period = utils.get_next_period(this_period)
        import_values.append(stats["import_value"])
        export_values.append(stats["export_value"])

    #print(time.time() - t1)
    return import_values, export_values


def demo():
    get_trade_stats_for_previous_year("FR", "202008", "901831")
    # comext_parser = COMEXTParser()
    # df = comext_parser.get_data_as_df(time_period="202008", hs6="901831")
    # import_value, import_kg, export_value, export_kg = get_trade_stats_for_country(
    #    df, "CN"
    # )
    # df = comext_parser.get_data_as_df(time_period="201908", hs6="901831")

    # import_value, import_kg, export_value, export_kg = get_trade_stats_for_country(
    #    df, "CN"
    # )

    # stats_1, stats_2 = get_trade_stats_for_2_countries(df, "FR", "CN")
    bb = 1


if __name__ == "__main__":
    demo()
