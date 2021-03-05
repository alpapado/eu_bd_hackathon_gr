import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import numpy as np
import utils

from itgs import ITGSParser
from comext import COMEXTParser


class BuildNetworkComext:
    def __init__(self, period, limit, product, MAP_DIM=1500):
        self.comext_object = COMEXTParser()
        self.period = period
        self.limit = limit
        self.product = product
        self.MAP_DIM = MAP_DIM

    def get_unique_countries(self, df):
        unique_countries = pd.concat(
            [df["DECLARANT_ISO"], df["PARTNER_ISO"]]).unique()
        return unique_countries

    def update(self, period, limit, product):
        self.period = period
        self.limit = limit
        self.product = product

    def get_directed_eu(self, percentile=0.5):
        df = self.comext_object.get_data_as_df(
            time_period=self.period, limit=self.limit, hs6=self.product
        )

        filter_value_euros = df['VALUE_IN_EUROS'].quantile(percentile)

        max_value_in_euros = df["VALUE_IN_EUROS"].astype(float).max()

        unique_countries = self.get_unique_countries(df)

        directed_elements = []

        directed_elements.append(
            {'classes': 'compound',
            "selectable": False,
            "locked": True,
            "data": {"id": "eu", "label": "Europe"}
            })

        for country in unique_countries:

            country_name = utils.get_country_name_from_iso_code(country)
            if country_name == "Unknown":
                continue

            x, y = utils.country_code_to_x_y(
                country, map_width=4 * self.MAP_DIM, map_height=self.MAP_DIM
            )
            if utils.is_country_in_europe(country):
                parent = "eu"
            else:
                parent = ""

            this_element = {
                "locked": True,
                "classes": "countries",
                "data": {
                    "id": country,
                    # utils.get_country_name_from_iso_code(country),
                    "label": country,
                    "parent": parent,
                },
                "position": {"x": x, "y": y},
            }
            directed_elements.append(this_element)

        for _, row in df.iterrows():
            if (
                utils.get_country_name_from_iso_code(
                    row["PARTNER_ISO"]) == "Unknown"
                or utils.get_country_name_from_iso_code(row["DECLARANT_ISO"])
                == "Unknown"
            ):
                continue

            if row['VALUE_IN_EUROS'] < filter_value_euros:
                continue

            if row["FLOW"] == 1:
                this_element = {
                    "data": {
                        "id": row["PARTNER_ISO"] + row["DECLARANT_ISO"],
                        "source": row["PARTNER_ISO"],
                        "target": row["DECLARANT_ISO"],
                        "value": row["VALUE_IN_EUROS"],
                        "quantity": row["QUANTITY_IN_KG"],
                    }
                }
            elif row["FLOW"] == 2:
                this_element = {
                    "data": {
                        "id": row["DECLARANT_ISO"] + row["PARTNER_ISO"],
                        "source": row["DECLARANT_ISO"],
                        "target": row["PARTNER_ISO"],
                        "value": row["VALUE_IN_EUROS"],
                        "quantity": row["QUANTITY_IN_KG"],
                    }
                }

                directed_elements.append(this_element)

        return directed_elements, max_value_in_euros, df


class BuildNetwork:
    def __init__(self, year, limit, product, MAP_DIM=500):
        self.itgs_object = ITGSParser()
        self.year = year
        self.limit = limit
        self.product = product
        self.MAP_DIM = MAP_DIM

    def get_unique_countries(self, df):
        unique_countries = pd.concat([df["ORIGIN"], df["DESTIN"]]).unique()
        return unique_countries

    def update(self, year, limit, product):
        self.year = year
        self.limit = limit
        self.product = product

    def get_directed(self):
        df = self.itgs_object.get_data_as_df(
            time_period=self.year, limit=self.limit, hs6=self.product
        )
        unique_countries = self.get_unique_countries(df)

        directed_elements = []
        for country in unique_countries:
            this_element = {
                "data": {
                    "id": country,
                    "label": utils.get_country_name_from_iso_code(country),
                }
            }
            directed_elements.append(this_element)

        for _, row in df.iterrows():
            this_element = {
                "data": {
                    "id": row["ORIGIN"] + row["DESTIN"],
                    "source": row["ORIGIN"],
                    "target": row["DESTIN"],
                    "label": row["OBS_VALUE"],
                }
            }
            directed_elements.append(this_element)

        return directed_elements

    def get_directed_eu(self):
        df = self.itgs_object.get_data_as_df(
            time_period=self.year, limit=self.limit, hs6=self.product
        )

        max_value_in_euros = df["OBS_VALUE"].astype(float).max()

        unique_countries = self.get_unique_countries(df)

        directed_elements = []

        directed_elements.append({"data": {"id": "eu", "label": "Europe"}})

        for country in unique_countries:
            x, y = utils.country_code_to_x_y(
                country, map_width=4 * self.MAP_DIM, map_height=self.MAP_DIM
            )
            if utils.is_country_in_europe(country):
                parent = "eu"
            else:
                parent = ""

            this_element = {
                "data": {
                    "id": country,
                    # utils.get_country_name_from_iso_code(country),
                    "label": country,
                    "parent": parent,
                },
                "position": {"x": x, "y": y},
            }
            directed_elements.append(this_element)

        for _, row in df.iterrows():
            this_element = {
                "data": {
                    "id": row["ORIGIN"] + row["DESTIN"],
                    "source": row["ORIGIN"],
                    "target": row["DESTIN"],
                    "label": float(row["OBS_VALUE"]),
                }
            }
            directed_elements.append(this_element)

        return directed_elements, max_value_in_euros
