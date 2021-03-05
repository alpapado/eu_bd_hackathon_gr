import dash
import dash_table
from datetime import date
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import numpy as np
import utils
import covid
import calendar

from comext import COMEXTParser
from frontend_utils import BuildNetworkComext
import trade

from scipy.stats import spearmanr

query_result = None

codes_to_products = {
    "901831": "Syringes",
    "901920": "Ventilators",
    "902000": "Surgical masks",
    "300650": "First aid kits",
    "220300": "Beer",
}
products = [
    {"label": "Syringes", "value": "901831"},
    {"label": "Ventilators", "value": "901902"},
    {"label": "Surgical masks", "value": "902000"},
    {"label": "First aid kits", "value": "300650"},
    {"label": "Beer", "value": "220300"},
]

products = [
        {"class": "4d", "label": "Instruments and appliances used in medical sciences", "value": "9018"},
        {"class": "6d", "label": "--> Syringes, with or without needles", "value": "901831"},
        {"class": "4d", "label": "Artificial respiration or other therapeutic respiration apparatus", "value": "9019"},
        {"class": "6d", "label": "--> Artificial respiration apparatus", "value": "901920"},
        {"class": "4d", "label": "Breathing appliances and gas masks", "value": "9020"},
        {"class": "6d", "label": "--> Surgical masks", "value": "902000"},
        {"class": "6d", "label": "--> First aid kits", "value": "300650"},
        {"class": "4d", "label": "Beer", "value": "220300"},
]

stylesheet = [
    {"selector": "node", "style": {"label": "data(id)"}},
    {
        "selector": "edge",
        "style": {
            # The default curve style does not work with certain arrows
            "curve-style": "bezier"
        },
    },
]


directed_elements = []
app = dash.Dash(__name__)


app.layout = html.Div(
    [
        html.Header(
            "CovEx: tracking Covid19-related Exchange",
            style={
                "width": "70vw",
                "font-size": "30px",
                "text-align": "center",
            },
        ),
        html.Div(
            children=[
                cyto.Cytoscape(
                    id="myDashboard",
                    layout={"name": "preset"},
                    style={
                        "height": "90vh",
                        "width": "75vw",
                        "border": "1px solid",
                        # "border-style": "solid",
                        "background-color": "rgba(182, 226, 237, 0.3)",
                    },
                    elements=directed_elements,
                    stylesheet=stylesheet,
                    minZoom=0.3,
                    maxZoom=1.0,
                ),
            ],
            style={"display": "inline-block"},
        ),
        html.P(id="cytoscape-tapNodeData-output"),
        html.P(id="cytoscape-tapEdgeData-output"),
        html.Div(
            [
                dcc.Graph(id="linePlot"),
                dcc.Graph(id="linePlot2"),
                dcc.Textarea(
                    id="correlation",
                    value="Correlation analysis...",
                    style={
                        "width": "20%",
                        "height": "150px",
                        "font-size": "20px",
                        "position": "absolute",
                        "top": "80%",
                        "left": "77%",
                    },
                ),
            ]
        ),
        html.Img(
            id="logo",
            src="https://www.anaplirotes.gr/wp-content/uploads/2019/09/elstat_logo.png",
            style={
                "position": "absolute",
                "top": "12%",
                "left": "87%",
                "max-width": "8%",
                "height": "auto",
            },
        ),
        html.Div(
            id="selectors",
            children=[
                html.Div(
                    children=[
                        html.P("Product category"),
                        dcc.Dropdown(
                            id="itemSelector",
                            value=products[0]["value"],
                            clearable=False,
                            options=[
                                {
                                    "label": name["label"].capitalize(),
                                    "value": name["value"],
                                }
                                for name in products
                            ],
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        # 'vertical-align': 'top',
                        'width': '100%',
                        #'height': '40%',
                    },
                ),
                # second column of first row
                html.Div(
                    children=[
                        html.P("Period"),
                        dcc.DatePickerSingle(
                            id="dateSelector",
                            min_date_allowed=date(2019, 1, 1),
                            max_date_allowed=date(2021, 12, 1),
                            initial_visible_month=date(2019, 1, 1),
                            date=date(2019, 1, 1),
                            display_format="M-Y",
                        ),
                    ]
                ),
                # html.Div(
                #     children=[
                #         dcc.Dropdown(
                #             id="periodSelector",
                #             value="201901",
                #             clearable=True,
                #             options=[
                #                 {"label": str(period), "value": period}
                #                 for period in ["201901", "202008"]
                #             ],
                #         ),
                #     ],
                #     style={  # 'display': 'inline-block',
                #         # 'vertical-align': 'top',
                #         # 'width': '10%'
                #     },
                # ),
                # third column of first row
                html.Div(
                    children=[
                        html.P("Limit"),
                        dcc.Dropdown(
                            id="queryLimitSelector",
                            value="100",
                            clearable=True,
                            options=[
                                {"label": str(limit), "value": limit}
                                for limit in [10, 100, 200, 500, 1000, "No limit"]
                            ],
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        # 'vertical-align': 'top',
                        "width": "30%",
                    },
                ),
            ],
            style={  # 'float': 'right',
                "width": "20%",
                # "border": "1px dashed",
                "border": "none",
                # "border-style": "groove",
                "position": "absolute",
                "top": "1.25%",
                "left": "77%",
                # 'display': 'inline-block',
                # 'vertical-align': 'top',
            },
        ),
        html.Div(
            id="country_details",
            children=[
                html.Div(
                    children=[
                        # html.P(id="cytoscape-mouseoverNodeData-output"),
                        # html.P(id="cytoscape-mouseoverEdgeData-output"),
                        dcc.Textarea(
                            id="text_area_1",
                            value="Click on a country to get more information.",
                            draggable=True,
                            style={
                                "width": "100%",
                                "height": "465px",
                                "font-size": "20px",
                            },
                        ),
                        html.Div(
                            id="text_area_1_output", style={"whiteSpace": "pre-line"}
                        ),
                    ],
                    style={  # 'display': 'inline-block',
                        # 'vertical-align': 'top',
                        # 'width': '13%'
                    },
                ),
                # html.Div(
                #     children=[
                #         # html.Div(
                #         #     id="text_area_1_output", style={"whiteSpace": "pre-line"}
                #         # ),
                #         dcc.Textarea(
                #             id="text_area_2",
                #             value="Click on an edge to find out more information.",
                #             draggable=True,
                #             style={"width": "100%", "height": "200px"},
                #         ),
                #         html.Div(
                #             id="text_area_2_output", style={"whiteSpace": "pre-line"}
                #         ),
                #     ],
                #     style={  # 'display': 'inline-block',
                #         # 'vertical-align': 'top',
                #         # 'width': '13%'
                #     },
                # ),
            ],
            style={
                "width": "20%",
                # "height": "30%",
                # 'border': '3px solid',
                # 'border-style': 'groove',
                "position": "absolute",
                "top": "32%",
                "left": "77%",
            },
        ),
    ]
)


@app.callback(
    Output("text_area_1", "value"),
    Output("linePlot", "figure"),
    Output("linePlot2", "figure"),
    Output("correlation", "value"),
    Input("myDashboard", "tapNodeData"),
    Input("dateSelector", "date"),
    Input("myDashboard", "selectedNodeData"),
    Input("itemSelector", "value"),
)
def displayTapNodeData(data, period, multidata, product_label):
    period = utils.convert_date_to_str(period)
    if multidata:
        if len(multidata) > 1 and len(multidata) == 2:

            if utils.check_if_eu_selected_multi(multidata):
                return ""

            trade_stats_1_2, trade_stats_2_1 = trade.get_trade_stats_for_2_countries(
                query_result, multidata[0]["id"], multidata[1]["id"]
            )

            country_1 = utils.get_country_name_from_iso_code(multidata[0]["id"])
            country_2 = utils.get_country_name_from_iso_code(multidata[1]["id"])

            accum_result = ""

            for country in multidata:
                print(country)
                covid_data = covid.get_covid_summary_for_country_for_period(
                    country["id"], period
                )

                trade_stats = trade.get_trade_stats_for_country(
                    query_result, country["id"]
                )

                result = "Stats for {} during {} of {}\n".format(
                    utils.get_country_name_from_iso_code(country["label"]),
                    calendar.month_name[int(period[4:])],
                    period[:4],
                )
                covid_str = "Covid19 stats:\n New cases {} \n Deaths {} \n Active cases {} (up {}% from previous period)\n".format(
                    int(covid_data["new_cases"]),
                    int(covid_data["deaths"]),
                    covid_data["active_cases"],
                    covid_data["diff_active_cases"],
                )

                trade_str = "Imports/Exports of {}:\n Total imports {:,}€ - {:,}kg\n Total exports {:,}€ - {:,}kg".format(
                    codes_to_products[product_label],
                    trade_stats["import_value"],
                    trade_stats["import_kg"],
                    trade_stats["export_value"],
                    trade_stats["export_kg"],
                )

                accum_result += result + "\n" + covid_str + "\n" + trade_str + "\n\n"

            trade_1_str = "{} trade of {} with {}: \n Imports {:,}€ - {:,}kg\n Exports {:,}€ - {:,}kg \n\n".format(
                country_1,
                codes_to_products[product_label],
                # product_label,
                country_2,
                trade_stats_1_2["import_value"],
                trade_stats_1_2["import_kg"],
                trade_stats_1_2["export_value"],
                trade_stats_1_2["export_kg"],
            )

            trade_2_str = "{} trade of {} with {}: \n Imports {:,}€ - {:,}kg\n Exports {:,}€ - {:,}kg \n".format(
                country_2,
                codes_to_products[product_label],
                country_1,
                trade_stats_2_1["import_value"],
                trade_stats_2_1["import_kg"],
                trade_stats_2_1["export_value"],
                trade_stats_2_1["export_kg"],
            )

            # t = np.arange(len(imports_year))

            # fig.add_trace(go.Scatter(x=t, y=imports_year, mode='lines+markers'))
            # fig = px.line(x=t, y=[imports_year, exports_year], labels={
            #              'x': 'Time (in months)', 'y': 'Imports/exports and Covid19 cases'})

            result = accum_result + trade_1_str + trade_2_str
            return result, go.Figure(), go.Figure(), "Correlation analysis..."

    if data:
        if utils.check_if_eu_selected_single(data):
            return ""
        # print(query_result)
        country_code = data["id"]
        covid_data = covid.get_covid_summary_for_country_for_period(
            country_code, period
        )

        trade_stats = trade.get_trade_stats_for_country(query_result, country_code)

        result = "Stats for {} during {} of {}\n".format(
            utils.get_country_name_from_iso_code(data["label"]),
            calendar.month_name[int(period[4:])],
            period[:4],
        )
        covid_str = "Covid19 stats:\n New cases {} \n Deaths {} \n Active cases {} (up {}% from previous period)\n\n".format(
            int(covid_data["new_cases"]),
            int(covid_data["deaths"]),
            covid_data["active_cases"],
            covid_data["diff_active_cases"],
        )

        trade_str = "Imports/Exports of {}:\n Total imports {:,}€ - {:,}kg\n Total exports {:,}€ - {:,}kg".format(
            codes_to_products[product_label],
            trade_stats["import_value"],
            trade_stats["import_kg"],
            trade_stats["export_value"],
            trade_stats["export_kg"],
        )

        result += covid_str
        result += trade_str

        imports_year, exports_year = trade.get_trade_stats_for_previous_year(
            data["label"], period, product_label
        )

        new_cases, deaths, active_cases = covid.get_covid_stats_for_previous_year(
            data["label"], period
        )

        imports_new, _ = spearmanr(imports_year, new_cases)
        imports_deaths, _ = spearmanr(imports_year, deaths)
        imports_active, _ = spearmanr(imports_year, active_cases)

        exports_new, _ = spearmanr(exports_year, new_cases)
        exports_deaths, _ = spearmanr(exports_year, deaths)
        exports_active, _ = spearmanr(exports_year, active_cases)

        correlation_str = "Spearman correlation analysis results:\n Imports vs New cases {:.3f}\n Imports vs Deaths {:.3f}\n Imports vs Active cases {:.3f}\n Exports vs New cases {:.3f}\n Exports vs Deaths {:.3f}\n Exports vs Active cases {:.3f}".format(
            imports_new,
            imports_deaths,
            imports_active,
            exports_new,
            exports_deaths,
            exports_active,
        )

        months = []
        this_period = period
        for i in range(13):
            months.append(this_period[:4] + "-" + this_period[4:])
            this_period = utils.get_previous_period(this_period)
        months = months[::-1]

        fig = go.Figure(
            layout={
                "title": {"text": "Temporal evolution of trade volume of "
                + codes_to_products[product_label]
                + " over last 12 months",
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'y': 0.9,
                        'x': 0.5,
                        },
                "xaxis_title": "Period",
                "yaxis_title": "Trade volume (€)",
            }
        )
        fig.add_trace(
            go.Scatter(
                x=months,
                y=imports_year,
                mode="lines+markers",
                name="Imports",
                line=dict(dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=months,
                y=exports_year,
                mode="lines+markers",
                name="Exports",
                line=dict(dash="dash"),
            )
        )

        fig2 = go.Figure(
            layout={
                "title": {'text': 'Temporal evolution of Covid19 data over last 12 months',
                          'xanchor': 'center',
                          'yanchor': 'top',
                          'y': 0.9,
                          'x': 0.5,
                         },
                "xaxis_title": "Period",
                "yaxis_title": "No. of (people)",
            }
        )

        fig2.add_trace(
            go.Scatter(
                x=months,
                y=new_cases,
                mode="lines+markers",
                name="New",
                line=dict(dash="dash"),
            )
        )
        fig2.add_trace(
            go.Scatter(x=months, y=deaths, mode="lines+markers", name="Deaths")
        )
        fig2.add_trace(
            go.Scatter(x=months, y=active_cases, mode="lines+markers", name="Active")
        )

        # fig = px.line(x=month, y=[imports_year, exports_year, new_cases, deaths, active_cases], labels={
        #              'x': 'Time (in months)', 'y': 'Imports/exports and Covid19 cases'})

        return result, fig, fig2, correlation_str

    return "Country details...", go.Figure(), go.Figure(), "Correlation analysis..."


# @app.callback(Output("text_area_2", "value"), Input("myDashboard", "tapEdgeData"))
# def displayTapEdgeData(data):
#     if data:
#         return (
#             "You recently clicked/tapped the edge between "
#             + data["source"].upper()
#             + " and "
#             + data["target"].upper()
#         )


# @app.callback(Output('cytoscape-mouseoverNodeData-output', 'children'),
#               Input('myDashboard', 'mouseoverNodeData'))
# def displayTapNodeData(data):
#     if data:
#         return "You recently hovered over the city: " + data['label']


# @app.callback(Output('cytoscape-mouseoverEdgeData-output', 'children'),
#               Input('myDashboard', 'mouseoverEdgeData'))
# def displayTapEdgeData(data):
#     if data:
#         return "You recently hovered over the edge between " + data['source'].upper() + " and " + data['target'].upper()


# @ app.callback(Output("myDashboard", "layout"))
# def update_layout(layout):
#     return {"name": layout, "animate": True}


@app.callback(
    Output("myDashboard", "elements"),
    Output("myDashboard", "stylesheet"),
    # Output("myDashboard", "query_result"),
    Input("itemSelector", "value"),
    # Input("periodSelector", "value"),
    Input("dateSelector", "date"),
    Input("queryLimitSelector", "value"),
)
def update_elements(value_item, value_period, value_limit):
    value_period = utils.convert_date_to_str(value_period)
    if value_limit == "No limit":
        bn = BuildNetworkComext(period=value_period, product=value_item, limit=None)
    else:
        bn = BuildNetworkComext(
            period=value_period, limit=value_limit, product=value_item
        )

    directed_elements, max_value_in_euros, df = bn.get_directed_eu()
    global query_result
    query_result = df

    opacity_string = "mapData(value, 0.2, {}, 0.1, 1)".format(max_value_in_euros)
    # print(opacity_string)

    stylesheet = [
        {
            "selector": ".countries",  # For all nodes
            "style": {
                "opacity": 1,
                "font-size": "40px",
                "label": "data(label)",  # Label of node to display
                "background-color": "rgba(0, 0, 0, 0)",
                "color": "#008B80",  # node label color
                "width": 10,
                "height": 10,
            },
        },
        {
            "selector": ".compound",
            "style": {
                "opacity": 1,
                "font-size": "40px",
                "label": "data(label)",  # Label of node to display
                # "background-color": "transparent",
                # "background-color": "rgba(182, 226, 237, 0)",
                # "color": "#008B80",  # node label color
                # "width": 5,
                # "height": 5,
            },
        },
        {
            "selector": "edge",  # For all edges
            "style": {
                "target-arrow-color": "#91091e",  # Arrow color
                "target-arrow-shape": "triangle",  # Arrow shape
                # "color": "#C5D3E2",  # edge color
                "opacity": opacity_string,  # must be function of EUROS
                "line-style": "dashed",
                "line-color": "#91091e",
                "edge-weight": 1,
                "arrow-scale": 1,  # Arrow size
                "curve-style": "bezier",
            },
        },
    ]

    return directed_elements, stylesheet


app.run_server(debug=True, use_reloader=True, port=8887)
