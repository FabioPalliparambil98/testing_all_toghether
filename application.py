from flask import Flask, render_template, request
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import pandas as pd
import hashtag
import live_tweets_graphs
from source import preprocessed_data, load_data, merge_data

application = Flask(__name__)

""" 
Data Imports for Covid Cases worldwide
"""

total_confirmed, total_death, total_recovered, df_pop = load_data()

(grouped_total_confirmed, grouped_total_recovered,
 grouped_total_death, timeseries_final, country_names) = preprocessed_data(total_confirmed, total_death,
                                                                           total_recovered)

final_df = merge_data(grouped_total_confirmed, grouped_total_recovered, grouped_total_death, df_pop)

df_general_filter = pd.read_csv('https://raw.githubusercontent.com/FabioPalliparambil98/cleaned-covid-dataset/main/general_covid.csv')
df_restriction_filter = pd.read_csv('https://raw.githubusercontent.com/FabioPalliparambil98/cleaned-covid-dataset/main/covid_restriction.csv')
df_vaccination_filter = pd.read_csv('https://raw.githubusercontent.com/FabioPalliparambil98/cleaned-covid-dataset/main/covid_vaccination.csv')


df_general_filter_sentiment = df_general_filter.copy()
df_restriction_filter_sentiment = df_restriction_filter.copy()
df_vaccination_filter_sentiment = df_vaccination_filter.copy()


df_general_filter['sentiment'].replace(0, 'negative', inplace=True)
df_general_filter['sentiment'].replace(1, 'positive', inplace=True)

df_restriction_filter['sentiment'].replace(0, 'negative', inplace=True)
df_restriction_filter['sentiment'].replace(1, 'positive', inplace=True)

df_vaccination_filter['sentiment'].replace(0, 'negative', inplace=True)
df_vaccination_filter['sentiment'].replace(1, 'positive', inplace=True)


"""
It displays the Home Pages of the Visualisations.
"""


@application.route('/')
def homepage():

    sentiment_general = sentiment_data(df_general_filter_sentiment)
    sentiment_vaccination = sentiment_data(df_restriction_filter_sentiment)
    sentiment_restriction = sentiment_data(df_vaccination_filter_sentiment)

    plot_general, plot_restriction, plot_vaccination, line_general, line_restriction,line_vaccination, all_line_scatters,scatter_circles,pie_general = hashtag.create_plot(hashtag.df_general_hash_tag,
                                                                           hashtag.df_restriction_hash_tag,
                                                                           hashtag.df_vaccination_hash_tag)
    plots = {'plot_general': plot_general,
             'plot_restriction': plot_restriction,
             'plot_vaccination': plot_vaccination,
             'line_general': line_general,
             'line_restriction': line_restriction,
             'line_vaccination': line_vaccination,
             'all_line_scatters': all_line_scatters,
             'scatter_circles': scatter_circles,
             'pie_general': pie_general}

    return render_template("index.html",
                           sentiment_general=sentiment_general,
                           sentiment_vaccination=sentiment_vaccination,
                           sentiment_restriction=sentiment_restriction,
                           plots=plots)


@application.route('/page_with_filters')
@application.route('/page_with_filters_after_request', methods=["GET", "POST"])
@application.route('/page_with_filters_after_sentiment', methods=["GET", "POST"])
def page_with_filters():
    days_in_weeks = df_general_filter['day_in_week'].unique()
    sentiment = df_general_filter['sentiment'].unique()

    if request.method == "GET":
        day = "Monday"

        sentiment_form = "negative"

        day_mask = df_general_filter["day_in_week"] == day
        sentiment_mask = df_general_filter["sentiment"] == sentiment_form
        sentiment_mask1 = df_restriction_filter["sentiment"] == sentiment_form
        sentiment_mask2 = df_vaccination_filter["sentiment"] == sentiment_form

        #
        weekday_plot = weekday_create_plot(df_general_filter[day_mask])
        sentiment_plot = sentiment_retweets(df_general_filter[sentiment_mask])

        retweet_count_visualisation = retweet_count(df_general_filter[sentiment_mask],
                                                    df_restriction_filter[sentiment_mask1],
                                                    df_vaccination_filter[sentiment_mask2])

        return render_template("page_with_filters.html", days_in_weeks=days_in_weeks, sentiment=sentiment,
                               weekday_plot=weekday_plot, sentiment_plot=sentiment_plot,
                               retweet_count_visualisation=retweet_count_visualisation)


def weekday_create_plot(df_1):
    """ Scatter """

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_1['sentiment'],
            y=df_1['retweetcount']
        ))


    day_graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return day_graphJSON
def sentiment_retweets(df_1):
    """ Scatter """

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_1['day_in_week'],
            y=df_1['retweetcount']
        ))


    day_graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return day_graphJSON


def retweet_count(df_general, df_restriction, df_vaccination):
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_general['day_in_week'],
            y=df_general['retweetcount'],
            name='Retweeted tweets in COVID-19 General'
        ))

    fig.add_trace(
        go.Bar(
            x=df_restriction['day_in_week'],
            y=df_restriction['retweetcount'],
            name='Retweeted tweets in COVID-19 Restriction'
        ))
    fig.add_trace(
        go.Bar(
            x=df_vaccination['day_in_week'],
            y=df_vaccination['retweetcount'],
            name='Retweeted tweets in COVID-19 Vaccination'
        ))
    retweet_count_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return retweet_count_json

"""
It displays the analysis of live tweets.
"""


@application.route('/live_tweets')
def live_tweets():
    line_graph, choropleth_map = live_tweets_graphs.live_tweet()
    return render_template("live_tweets.html", choropleth_map=choropleth_map,line_graph=line_graph)


"""
It displays the analysis of live tweets.
"""


@application.route('/contact', methods=["GET", "POST"])
def contact_page():
    if request.method == "GET":

        return render_template('contact.html')

    elif request.method == "POST":

        name = request.form["txtName"]
        email = request.form["txtEmail"]
        phone = request.form["txtPhone"]
        message = request.form["txtMsg"]
        print(name, email, phone, message)

        return render_template('test.html')


"""
It displays the analysis of live tweets.
"""


@application.route('/covidcases')
def covidcases():
    total_all_confirmed = total_confirmed[total_confirmed.columns[-1]].sum()
    total_all_recovered = total_recovered[total_recovered.columns[-1]].sum()
    total_all_deaths = total_death[total_death.columns[-1]].sum()

    df = final_df
    df.index = df['Country/Region']
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["confirmed"],
            name="# of confirmed cases",
            marker_color='#39ac39',
            opacity=1
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["cases/million"],
            mode="lines",
            name="cases/million",
            marker_color='#b23434',
            opacity=0.7
        ),
        secondary_y=True
    )

    # Add figure title
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=0.93),
        title={
            'text': '<span style="font-size: 20px;">Global aggregate cases</span><br><span style="font-size: 10px;">(click and drag)</span>',
            'y': 0.97,
            'x': 0.45,
            'xanchor': 'center',
            'yanchor': 'top'},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        width=1500, height=700
    )

    # Set x-axis title
    fig.update_xaxes(tickangle=45)

    # Set y-axes titles
    fig.update_yaxes(title_text="# of confirmed cases",
                     secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text="cases/millions", tickangle=45,
                     secondary_y=True, showgrid=False)
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    plot_global_cases_per_country = plot_json

    context = {'plot_global_cases_per_country': plot_global_cases_per_country}
    return render_template('covidcases.html', context=context, total_all_confirmed=total_all_confirmed,
                           total_all_recovered=total_all_recovered,
                           total_all_deaths=total_all_deaths)



"""
It get the sentimental value
"""


def sentiment_data(df):
    df_sentiment = df['sentiment'].value_counts()
    negative = df_sentiment.loc[0]
    positive = df_sentiment.loc[1]
    if negative > positive:
        return "negative"
    else:
        return "positive"


if __name__ == '__main__':
    application.run()
