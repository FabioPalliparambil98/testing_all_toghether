import json
import string
import nltk
import pandas as pd
import plotly.graph_objects as go
import plotly
import re


"""
Uncleaned data on COVID-19 in General
"""

df_general = pd.read_csv(
    'https://raw.githubusercontent.com/FabioPalliparambil98/covid-dataset/main/combined_generaltweets.csv')

df_general["tweetcreatedts"] = pd.to_datetime(df_general["tweetcreatedts"])
df_general['Month'] = df_general.tweetcreatedts.dt.month
df_general['Hour'] = df_general.tweetcreatedts.dt.hour
df_general['day_in_week'] = df_general.tweetcreatedts.dt.weekday
df_general['day'] = df_general.tweetcreatedts.dt.day
df_general['day_in_week'].replace(0, 'Monday',inplace=True)
df_general['day_in_week'].replace(1, 'Tuesday',inplace=True)
df_general['day_in_week'].replace(2, 'Wednesday',inplace=True)
df_general['day_in_week'].replace(3, 'Thursday',inplace=True)
df_general['day_in_week'].replace(4, 'Friday',inplace=True)
df_general['day_in_week'].replace(5, 'Saturday',inplace=True)
df_general['day_in_week'].replace(6, 'Sunday',inplace=True)

"""
Uncleaned data on COVID-19 Restriction
"""

df_restriction = pd.read_csv(
    'https://raw.githubusercontent.com/FabioPalliparambil98/covid-dataset/main/combined_restrictiontweets.csv')

df_restriction["tweetcreatedts"] = pd.to_datetime(df_restriction["tweetcreatedts"])
df_restriction['Month'] = df_restriction.tweetcreatedts.dt.month
df_restriction['Hour'] = df_restriction.tweetcreatedts.dt.hour
df_restriction['day_in_week'] = df_restriction.tweetcreatedts.dt.weekday
df_restriction['day'] = df_restriction.tweetcreatedts.dt.day

df_restriction['day_in_week'].replace(0, 'Monday',inplace=True)
df_restriction['day_in_week'].replace(1, 'Tuesday',inplace=True)
df_restriction['day_in_week'].replace(2, 'Wednesday',inplace=True)
df_restriction['day_in_week'].replace(3, 'Thursday',inplace=True)
df_restriction['day_in_week'].replace(4, 'Friday',inplace=True)
df_restriction['day_in_week'].replace(5, 'Saturday',inplace=True)
df_restriction['day_in_week'].replace(6, 'Sunday',inplace=True)




"""
Uncleaned data on COVID-19 Vaccination
"""

df_vaccination = pd.read_csv(
    'https://raw.githubusercontent.com/FabioPalliparambil98/covid-dataset/main/combined_vaccinationtweets.csv')

df_vaccination["tweetcreatedts"] = pd.to_datetime(df_vaccination["tweetcreatedts"])
df_vaccination['Month'] = df_vaccination.tweetcreatedts.dt.month
df_vaccination['Hour'] = df_vaccination.tweetcreatedts.dt.hour
df_vaccination['day_in_week'] = df_vaccination.tweetcreatedts.dt.weekday
df_vaccination['day'] = df_vaccination.tweetcreatedts.dt.day

df_vaccination['day_in_week'].replace(0, 'Monday',inplace=True)
df_vaccination['day_in_week'].replace(1, 'Tuesday',inplace=True)
df_vaccination['day_in_week'].replace(2, 'Wednesday',inplace=True)
df_vaccination['day_in_week'].replace(3, 'Thursday',inplace=True)
df_vaccination['day_in_week'].replace(4, 'Friday',inplace=True)
df_vaccination['day_in_week'].replace(5, 'Saturday',inplace=True)
df_vaccination['day_in_week'].replace(6, 'Sunday',inplace=True)



"""
Function for collecting all the Hashtag
"""


def collectHashtag(x):
    hashtags = []
    for i in x:
        ht = re.findall(r"#(\w+)", i)
        hashtags.append(ht)
    return hashtags


"""
Function for collecting hashed into multiple dataframe
"""


def clean_hastag(text):
    text = "".join([char for char in text if char not in string.punctuation])
    text = text.lower()
    return text


def hastag_dataframe(df):

    HT_general = collectHashtag(df['text'])
    HT_general = sum(HT_general, [])
    general_tag = nltk.FreqDist(HT_general)
    hashtag_general = pd.DataFrame({'Hashtag': list(general_tag.keys()), 'Count': list(general_tag.values())})
    hashtag_general['Hashtag'] = hashtag_general['Hashtag'].apply(lambda x: clean_hastag(x))
    hashtag_general['Hashtag'] = hashtag_general['Hashtag'].drop_duplicates()
    hashtag_general = hashtag_general.dropna()
    hashtag_general = hashtag_general.nlargest(columns='Count', n=15)
    return hashtag_general


df_general_hash_tag = hastag_dataframe(df_general)
df_restriction_hash_tag = hastag_dataframe(df_restriction)
df_vaccination_hash_tag = hastag_dataframe(df_vaccination)


def create_plot(df_general_hashtag, df_restriction_hashtag, df_vaccination_hashtag):
    scatter_general = [go.Bar(
        x=df_general_hashtag['Hashtag'],
        y=df_general_hashtag['Count'],
        marker_color='lightsalmon',
        text=df_general_hashtag['Count'],
        textposition='auto'
    )
    ]
    graph_general = go.Figure(scatter_general)
    graph_general.update_layout(
        title='General Frequency Tweet Count',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Word Frequency Count',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        xaxis_tickangle=-45,
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )

    scatter_restriction = [go.Bar(
        x=df_restriction_hashtag['Hashtag'],
        y=df_restriction_hashtag['Count'],
        marker_color='lightsalmon',
        text=df_restriction_hashtag['Count'],
        textposition='auto'
    )
    ]
    graph_restriction = go.Figure(scatter_restriction)
    graph_restriction.update_layout(
        title='restriction Frequency Tweet Count',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Word Frequency Count',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        xaxis_tickangle=-45,
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )

    scatter_vaccination = [go.Bar(
        x=df_vaccination_hashtag['Hashtag'],
        y=df_vaccination_hashtag['Count'],
        marker_color='lightsalmon',
        text=df_vaccination_hashtag['Count'],
        textposition='auto'
    )
    ]
    graph_vaccination = go.Figure(scatter_vaccination)
    graph_vaccination.update_layout(
        title='General Frequency Tweet Count',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Word Frequency Count',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        xaxis_tickangle=-45,
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )
    """ Scatter """

    # Create a trace
    scatter_line_genreal = [go.Scatter(
        x=df_general_hashtag['Hashtag'],
        y=df_general_hashtag['Count'],
        mode='lines+markers',
        name='lines+markers',
        marker_color='rgba(255, 182, 193, .9)'
        # mode='markers'
    )]

    """ Scatter """

    # Create a trace
    scatter_line_restriction = [go.Scatter(
        x=df_restriction_hashtag['Hashtag'],
        y=df_restriction_hashtag['Count'],
        mode='lines+markers',
        name='lines+markers',
        marker_color='rgba(255, 182, 193, .9)'
        # mode='markers'
    )]

    """ Scatter """

    # Create a trace
    scatter_line_vaccination = [go.Scatter(
        x=df_vaccination_hashtag['Hashtag'],
        y=df_vaccination_hashtag['Count'],
        mode='lines+markers',
        name='lines+markers',
        marker_color='rgba(255, 182, 193, .9)'
        # mode='markers'
    )]

    """ all toghether"""
    all_scatter_line = go.Figure()

    all_scatter_line.add_trace(
        go.Bar(
            x=df_general_hashtag['Hashtag'],
            y=df_general_hashtag['Count'],
            name='COVID-19 General Hashtag'
        ))

    all_scatter_line.add_trace(
        go.Bar(
            x=df_vaccination_hashtag['Hashtag'],
            y=df_vaccination_hashtag['Count'],
            name='COVID-19 Restriction Hashtag'
        ))
    all_scatter_line.add_trace(
        go.Bar(
            x=df_restriction_hashtag['Hashtag'],
            y=df_restriction_hashtag['Count'],
            name='COVID-19 Vaccination Hashtag'
        ))

    Scatters = go.Figure(data=go.Scatter(
        x=df_general_hashtag['Hashtag'],
        y=df_general_hashtag['Count'],
        mode='markers',
        marker=dict(size=[100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30],
                    color=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
    ))

    # labels = ['Oxygen', 'Hydrogen', 'Carbon_Dioxide', 'Nitrogen']
    # values = [4500, 2500, 1053, 500]
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']

    Pie = go.Figure(data=[go.Pie(labels=df_general_hashtag['Hashtag'],
                                 values=df_general_hashtag['Count'],
                                 textinfo='label+percent',
                                 insidetextorientation='radial',
                                 hole=.2)])

    general_JSON = json.dumps(scatter_general, cls=plotly.utils.PlotlyJSONEncoder)
    restriction_JSON = json.dumps(scatter_restriction, cls=plotly.utils.PlotlyJSONEncoder)
    vaccination_JSON = json.dumps(scatter_vaccination, cls=plotly.utils.PlotlyJSONEncoder)
    line_genreal_JSON = json.dumps(scatter_line_genreal, cls=plotly.utils.PlotlyJSONEncoder)
    line_restriction_JSON = json.dumps(scatter_line_restriction, cls=plotly.utils.PlotlyJSONEncoder)
    line_vaccination_JSON = json.dumps(scatter_line_vaccination, cls=plotly.utils.PlotlyJSONEncoder)
    all_scatter_lineJSON = json.dumps(all_scatter_line, cls=plotly.utils.PlotlyJSONEncoder)
    Scatters_JSON = json.dumps(Scatters, cls=plotly.utils.PlotlyJSONEncoder)
    Pie_json = json.dumps(Pie, cls=plotly.utils.PlotlyJSONEncoder)

    return general_JSON, restriction_JSON, vaccination_JSON, line_genreal_JSON, line_restriction_JSON, line_vaccination_JSON, all_scatter_lineJSON, Scatters_JSON, Pie_json



