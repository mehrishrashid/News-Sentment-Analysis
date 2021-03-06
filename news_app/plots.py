import json
import plotly
import os
import json
import calmap
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt, mpld3
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import pickle

mapbox_token = os.getenv("mapbox_token")
# FILE_PATH = os.path.join("news_app", "static", "data", "headlines_scores_keywords.csv")

def article_vs_headline_plot(df_in):
    # Read in data
    # df = pd.read_csv(FILE_PATH)
    df = df_in
    df = df[["headline", "headline_score", "article_score", "news_desk"]].loc[
        (df["headline_score"] != 0)
        & (df["article_score"] != 0)
        & (df["section_name"] != "Business Day")
        & (df["news_desk"] != "Media")
        & (df["news_desk"] != "National")
    ]
    # ['National' 'Business' 'Politics' 'Science' 'Climate']

    # Line colors
    lines_colors_dict = {
        "Society": "rgba(30, 144, 255, 0.7)",  # "dodgerblue",
        "Business": "rgba(255, 215, 0, 0.7)",  # "gold",
        "Politics": "rgba(178, 34, 34, 0.7)",  # "firebrick",
        "Science": "rgba(34, 139, 34, 0.7)",  # "forestgreen",
        "Climate": "rgba(255, 140, 0, 0.7)",  # "darkorange"
        "Arts&Leisure": "rgba(138, 43, 226, 0.7)",  # "blueviolet",
    }

    # Marker fill colors with 50% opacity
    markers_colors_dict = {
        "Society": "rgba(30, 144, 255, 0.2)",  # "dodgerblue",
        "Business": "rgba(255, 215, 0, 0.2)",  # "gold",
        "Politics": "rgba(178, 34, 34, 0.2)",  # "firebrick",
        "Science": "rgba(34, 139, 34, 0.2)",  # "forestgreen",
        "Climate": "rgba(255, 140, 0, 0.2)",  # "darkorange"
        "Arts&Leisure": "rgba(138, 43, 226, 0.2)",  # "blueviolet",
    }

    df["markers_colors"] = df["news_desk"].map(markers_colors_dict)
    df["lines_colors"] = df["news_desk"].map(lines_colors_dict)

    df.head(10)

    fig = go.Figure()
    i = 0
    for desk in df["news_desk"].unique():
        df_current = df.loc[df["news_desk"] == desk]
        fig.add_trace(
            px.density_contour(df_current, x="headline_score", y="article_score",)["data"][
                0
            ]
        )
        fig.data[i * 3].update(
            name=desk,
            line={
                "color": df_current["lines_colors"]
                .loc[df_current["news_desk"] == desk]
                .unique()[0],
                "width": 1,
            },
            legendgroup=desk,
            showlegend=True,
            hovertemplate="",
            hoverinfo="skip",
        )

        fig.add_trace(
            go.Scatter(x=df_current["headline_score"], y=df_current["article_score"],)
        )
        fig.data[(i * 3) + 1].update(
            mode="markers",
            marker={
                "color": df_current["markers_colors"],
                "line": {"color": "rgba(105, 105, 105, .5)", "width": 0.3},  # dimgrey
            },
            text=desk,
            hovertemplate="Headline: %{x}<br>Article: %{y}<extra></extra>",
            legendgroup=desk,
            showlegend=False,
        )

        MODELS_FILEPATH = os.path.join("news_app", "static", "resources", "saved_models")
        pickle_filename = f"pickle_model_{desk}.pkl"
        with open(os.path.join(MODELS_FILEPATH, pickle_filename), "rb") as file:
            model = pickle.load(file)

        x_trace = [-1, 1]
        y_trace = [model.predict([[-1]])[0], model.predict([[1]])[0]]

        fig.add_trace(
            go.Scatter(
                x=x_trace,
                y=y_trace,
                mode="lines",
                line={"color": lines_colors_dict[desk], "width": 2, "dash": "dot",},
                legendgroup=desk,
                name=desk,
                showlegend=False,
                text=df_current["news_desk"],
                hovertemplate="%{text}<extra></extra>",
            )
        )
        i += 1

    fig.layout.update(
        title="Article vs Headline Score",
        title_x=0.5,
        xaxis={"title": {"text": "Headline Scores"}},
        yaxis={"title": {"text": "Article Scores"}},
        paper_bgcolor="white",
        plot_bgcolor="ghostwhite",
        legend={"title": {"text": "<b>News Desks<b>"}}
    )

    fig_data = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return fig_data


def calendar_heatmap():
    
    cal_heatmap_df = pd.read_csv(os.path.join("news_app", "static", "data", "calendar_heatmap_new.csv"))

    cal_heatmap_df["date"] = cal_heatmap_df["date"].apply(lambda x: datetime.strptime(x, "%m/%d/%Y"))
    cal_heatmap_df["top_headlines"] = cal_heatmap_df["top_headlines"].apply(lambda x: eval(x))

    df2015 = cal_heatmap_df.loc[cal_heatmap_df["date"].apply(lambda dt: dt.year == 2015)]
    df2016 = cal_heatmap_df.loc[cal_heatmap_df["date"].apply(lambda dt: dt.year == 2016)]
    df2017 = cal_heatmap_df.loc[cal_heatmap_df["date"].apply(lambda dt: dt.year == 2017)]

    color_scale = [
        [0, "darkred"],
        [.1, "darkred"],
        [.1, "firebrick"],
        [.2, "firebrick"],
        [.2, "indianred"],
        [.3, "indianred"],
        [.3, "lightcoral"],
        [.4, "lightcoral"],
        [.4, "mistyrose"],
        [.475, "mistyrose"],
        [.475, "white"],
        [.525, "white"],
        [.525, "honeydew"],
        [.6, "honeydew"],
        [.6, "palegreen"],
        [.7, "palegreen"],
        [.7, "limegreen"],
        [.8, "limegreen"],
        [.8, "forestgreen"],
        [.9, "forestgreen"],
        [.9, "darkgreen"],
        [1, "darkgreen"],
    ]

    trace2015 = {
        "z": df2015["avg_score"],
        "x": df2015["date"],
        "y": df2015["news_desk"],
        "type": "heatmap",
        "colorscale": color_scale,
        "showscale": True,
        "text": df2015["top_headlines"],
        "hovertemplate": '<b>Most emotional %{y} headlines for %{x}</b>:' +
            '<br>%{text.score[0]} | %{text.headline[0]}' +
            '<br>%{text.score[1]} | %{text.headline[1]}' +
            '<br>%{text.score[2]} | %{text.headline[2]}' +
            "<br><b>Today's Average: %{z}</b><extra></extra>", 
        "showlegend": False,
        "name": "",
    }

    trace2016 = {
        "z": df2016["avg_score"],
        "x": df2016["date"],
        "y": df2016["news_desk"],
        "xaxis": "x2",
        "yaxis": "y2",
        "type": "heatmap",
        "colorscale": color_scale,
        "showscale": False,
        "text": df2016["top_headlines"],
        "hovertemplate": '<b>Most emotional %{y} headlines for %{x}</b>:' +
            '<br>%{text.score[0]} | %{text.headline[0]}' +
            '<br>%{text.score[1]} | %{text.headline[1]}' +
            '<br>%{text.score[2]} | %{text.headline[2]}' +
            "<br><b>Today's Average: %{z}</b><extra></extra>", 
        "showlegend": False,
        "name": "",
    }

    trace2017 = {
        "z": df2017["avg_score"],
        "x": df2017["date"],
        "y": df2017["news_desk"],
        "xaxis": "x3",
        "yaxis": "y3",
        "type": "heatmap",
        "colorscale": color_scale,
        "showscale": False,
        "text": df2017["top_headlines"],
        "hovertemplate": '<b>Most emotional %{y} headlines for %{x}:</b>' +
            '<br>%{text.score[0]} | %{text.headline[0]}' +
            '<br>%{text.score[1]} | %{text.headline[1]}' +
            '<br>%{text.score[2]} | %{text.headline[2]}' +
            "<br><b>Today's Average: %{z}</b><extra></extra>", 
        "showlegend": False,
        "name": "",
    }

    plot_data = [trace2015, trace2016, trace2017]

    plot_layout = {
        "title": "Average Daily Headline Sentiment by News Desk",
        "xaxis_nticks": 12,
        "grid": {
            "rows": 3, 
            "columns": 1, 
            "pattern": "independent",
            "roworder": "top to bottom",
        },
        "margin": {"l":100},
        "plot_bgcolor": "ghostwhite",
        "height": 600,
    }

    heatmap_data = json.dumps(plot_data, cls=plotly.utils.PlotlyJSONEncoder)
    heatmap_layout = json.dumps(plot_layout, cls=plotly.utils.PlotlyJSONEncoder)
    
    return heatmap_data, heatmap_layout


def box_plots(df_in):
    # Read in data
    # df = pd.read_csv(FILE_PATH)

    df = df_in[["article_score", "news_desk"]].loc[
        (df_in["article_score"] != 0) & 
        (df_in["section_name"] != "Business Day") &
        (df_in["news_desk"] != "Media") &
        (df_in["news_desk"] != "National")
    ]
    # ['National' 'Business' 'Politics' 'Science' 'Climate']
    
    # Box colors
    box_colors_dict = { 
        "Society": "dodgerblue",
        "Business": "gold",
        "Politics": "firebrick",
        "Science": "forestgreen",
        "Climate": "darkorange",
        "Arts&Leisure": "blueviolet",
    }

    df["markers_colors"] = df["news_desk"].map(box_colors_dict)

    plot_data = []

    for desk in df["news_desk"].unique():
        scatter_trace = {
            "y": df["article_score"].loc[df["news_desk"] == desk],
            "type": "box",
            "name": desk,
            "marker": {
                "color": box_colors_dict[desk],
            },
            "boxpoints": "outliers",
            "showlegend": True,
        }
        plot_data.append(scatter_trace)

        plot_layout = {
            "title": "Article Score Statistics",
            "hovermode": "closest",
            "paper_bgcolor": "white",
            "plot_bgcolor": "ghostwhite",
            "legend": {"title": {"text": "<b>News Desks</b>"}},
        }

    boxplot_data = json.dumps(plot_data, cls=plotly.utils.PlotlyJSONEncoder)
    boxplot_layout = json.dumps(plot_layout, cls=plotly.utils.PlotlyJSONEncoder)
    
    return boxplot_data, boxplot_layout

def lat_lon_heatmap():
    GEOCODE_DATA = os.path.join("news_app", "static", "data", "geocoded_headlines_scores_keywords.csv")
    df = pd.read_csv(GEOCODE_DATA).dropna(how="any")

    def location(x):
        location_details = (
            x.replace("'", "$")
            .replace('"', "'")
            .replace("$", '"')
            .replace("""'Provence-Alpes-C??te d"Azur'""", '"Provence-Alpes-C??te dAzur"')
            .replace(
                """'Commune Petite Rivi??re de l"Artibonite'""",
                '"Commune Petite Rivi??re de lArtibonite"',
            )
        )
        location_dict = json.loads(location_details)
        location_string = ""
        if location_dict["city"]:
            location_string += location_dict["city"] + ", "
        if location_dict["state"]:
            location_string += location_dict["state"] + ", "
        if location_dict["country"]:
            location_string += location_dict["country"]
        return location_string
    
    df["latitude"] = df["lat_lon"].apply(lambda x: eval(x)[0])
    df["longitude"] = df["lat_lon"].apply(lambda x: eval(x)[1])
    df["date"] = df["pub_date"].apply(lambda x: datetime.strptime(x, "%m/%d/%Y"))
    df["month"] = df["date"].apply(lambda x: x.to_period("M"))
    df["month_str"] = df["month"].apply(lambda x: str(x))
    df["location_details_dict"] = df["location_details"].apply(lambda x: location(x))
    print(df.head())

    fig2 = px.scatter_mapbox(
        df,
        lon="longitude",
        lat="latitude",
        custom_data=["headline", "location_details_dict", "article_score"],
        color="article_score",
        color_continuous_scale="rdylgn",
        opacity=0.6,
        mapbox_style="light",
        zoom=1,
        hover_name="headline",
        hover_data={
            "article_score": True,
            "longitude": False,
            "latitude": False,
            "month_str": False,
        },
        animation_frame="month_str",
        height=500,
        width=800,
        center={"lat": 35, "lon": -60},
    )

    fig2.update_traces(
        mode="markers",
        marker={"size": 18,},
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Article Score: %{customdata[2]:.4f}",
    )

    for frame in fig2.frames:
        frame["data"][0].update(
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Article Score: %{customdata[2]:.4f}",
        )

    fig2.update_layout(
        title={"text": "Headlines Around the World (2015-2017)"},
        margin={"t": 30, "b": 5, "l": 5, "r": 5},
        mapbox_accesstoken=mapbox_token,
        sliders=[{"currentvalue": {"prefix": "Month: "}}],
    )

    fig2.update_coloraxes(colorbar_title={"text": "Article Sentiment"},)

    fig2.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000

    fig2_json = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return fig2_json


def linechart():
    linechart_df = pd.read_csv(os.path.join("news_app", "static", "data", "calendar_heatmap_new.csv"))

    linechart_df["date"] = linechart_df["date"].apply(
        lambda x: datetime.strptime(x, "%m/%d/%Y")
    )
    linechart_df["top_headlines"] = linechart_df["top_headlines"].apply(lambda x: eval(x))

    linechart_df.head()
    linechart_df["news_desk"].unique()

    lines_colors_dict2 = {
        "National": "rgba(25, 25, 112, 1)",  # "midnightblue",
        "Business": "rgba(255, 215, 0, 1)",  # "gold",
        "Science": "rgba(34, 139, 34, 1)",  # "forestgreen",
        "Arts&Leisure": "rgba(138, 43, 226, 1)",  # "blueviolet",
        "Society": "rgba(30, 144, 255, 1)",  # "dodgerblue",
        "Politics": "rgba(178, 34, 34, 1)",  # "firebrick",
        "Climate": "rgba(255, 140, 0, 1)",  # "darkorange",
    }

    visible_dict = {
        "Business": [True, False, False, False, False, False, False, False],
        "National": [False, True, False, False, False, False, False, False],
        "Arts&Leisure": [False, False, True, False, False, False, False, False],
        "Science": [False, False, False, True, False, False, False, False],
        "Society": [False, False, False, False, True, False, False, False],
        "Politics": [False, False, False, False, False, True, False, False],
        "Climate": [False, False, False, False, False, False, True, False],
    }

    fig3 = go.Figure()
    buttons = []

    for desk in linechart_df["news_desk"].unique():
        df_current = linechart_df.loc[linechart_df["news_desk"] == desk]

        fig3.add_trace(
            go.Scatter(
                x=df_current["date"],
                y=df_current["avg_score"],
                text=df_current["top_headlines"],
                customdata=df_current["news_desk"],
                name=desk,
                line={"color": lines_colors_dict2[desk]},
                visible=False,
                hovertemplate="<b>Most emotional %{customdata} headlines for %{x|%a %b %d, %Y}</b>:"
                + "<br>%{text.score[0]} | %{text.headline[0]}"
                + "<br>%{text.score[1]} | %{text.headline[1]}"
                + "<br>%{text.score[2]} | %{text.headline[2]}"
                + "<br><b>Today's Average: %{y}</b><extra></extra>",
            )
        )
        buttons.append(
            {
                "label": desk,
                "method": "update",
                "args": [
                    {"visible": visible_dict[desk]},
                    {"title": f"Average Daily Headline Sentiment for {desk} News"},
                ],
            }
        )

    fig3.data[0].update(visible=True)

    fig3.update_layout(
        title="Average Daily Headline Sentiment for Business News",
        title_x=0.5,
        xaxis={"title": {"text": "Date"}},
        yaxis={"title": {"text": "Average Headline Score"}},
        paper_bgcolor="white",
        plot_bgcolor="ghostwhite",
    )

    fig3.update_xaxes(
        range=[linechart_df["date"].min(), linechart_df["date"].max()],
        tickformat="%a %b %d, %Y")
    fig3.update_yaxes(range=[-1, 1])

    fig3.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "active": 0,
                "x": .8,
                "y": 1.15,
                "buttons": buttons,
            }
        ]
    )

    fig3_json = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    return fig3_json