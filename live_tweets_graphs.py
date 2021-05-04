import os

import settings
import pandas as pd
import time
import itertools
import math
import json
import plotly
import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import re
import nltk
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import psycopg2

# Filter constants for states in US
STATES = ['Alabama', 'AL', 'Alaska', 'AK', 'American Samoa', 'AS', 'Arizona', 'AZ', 'Arkansas', 'AR', 'California',
          'CA', 'Colorado', 'CO', 'Connecticut', 'CT', 'Delaware', 'DE', 'District of Columbia', 'DC',
          'Federated States of Micronesia', 'FM', 'Florida', 'FL', 'Georgia', 'GA', 'Guam', 'GU', 'Hawaii', 'HI',
          'Idaho', 'ID', 'Illinois', 'IL', 'Indiana', 'IN', 'Iowa', 'IA', 'Kansas', 'KS', 'Kentucky', 'KY', 'Louisiana',
          'LA', 'Maine', 'ME', 'Marshall Islands', 'MH', 'Maryland', 'MD', 'Massachusetts', 'MA', 'Michigan', 'MI',
          'Minnesota', 'MN', 'Mississippi', 'MS', 'Missouri', 'MO', 'Montana', 'MT', 'Nebraska', 'NE', 'Nevada', 'NV',
          'New Hampshire', 'NH', 'New Jersey', 'NJ', 'New Mexico', 'NM', 'New York', 'NY', 'North Carolina', 'NC',
          'North Dakota', 'ND', 'Northern Mariana Islands', 'MP', 'Ohio', 'OH', 'Oklahoma', 'OK', 'Oregon', 'OR',
          'Palau', 'PW', 'Pennsylvania', 'PA', 'Puerto Rico', 'PR', 'Rhode Island', 'RI', 'South Carolina', 'SC',
          'South Dakota', 'SD', 'Tennessee', 'TN', 'Texas', 'TX', 'Utah', 'UT', 'Vermont', 'VT', 'Virgin Islands', 'VI',
          'Virginia', 'VA', 'Washington', 'WA', 'West Virginia', 'WV', 'Wisconsin', 'WI', 'Wyoming', 'WY']
STATE_DICT = dict(itertools.zip_longest(*[iter(STATES)] * 2, fillvalue=""))
INV_STATE_DICT = dict((v, k) for k, v in STATE_DICT.items())

'''
This complex plot shows the latest Twitter data within 20 mins and will automatically update.
'''


def live_tweet():
    while True:


        DATABASE_URL = os.environ['DATABASE_URL']
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        # Load data from MySQL
        timenow = (datetime.datetime.utcnow() - datetime.timedelta(hours=0, minutes=20)).strftime('%Y-%m-%d %H:%M:%S')
        query = "SELECT id_str, text, created_at, polarity, user_location FROM {} WHERE created_at >= '{}' " \
            .format(settings.table_name, timenow)
        df = pd.read_sql(query, con=connection)


        df = pd.read_sql(query, con=connection)
        # UTC for date time at default
        df['created_at'] = pd.to_datetime(df['created_at'])





        '''
        Plot the Line Chart
        '''
        line_chart = go.Figure()
        # Clean and transform data to enable time series
        result = df.groupby([pd.Grouper(key='created_at', freq='2s'), 'polarity']).count().unstack(fill_value=0).stack().reset_index()
        result = result.rename(columns={"id_str": "Num of '{}' mentions".format(settings.data_on_word[0]), "created_at": "Time in UTC"})
        time_series = result["Time in UTC"][result['polarity']==0].reset_index(drop=True)
        line_chart.add_trace(go.Scatter(
            x=time_series,
            y=result["Num of '{}' mentions".format(settings.data_on_word[0])][result['polarity'] == 0].reset_index(drop=True),
            name="Neural",
            opacity=0.8))
        line_chart.add_trace(go.Scatter(
            x=time_series,
            y=result["Num of '{}' mentions".format(settings.data_on_word[0])][result['polarity'] == -1].reset_index(drop=True),
            name="Negative",
            opacity=0.8))
        line_chart.add_trace(go.Scatter(
            x=time_series,
            y=result["Num of '{}' mentions".format(settings.data_on_word[0])][result['polarity'] == 1].reset_index(drop=True),
            name="Positive",
            opacity=0.8))
        line_chart.update_layout(title_text="Live Sentiment on COVID-19", title_font_size=20)

        '''
        Plot
        the
        Bar
        Chart
        '''
        # content = ' '.join(df["text"])
        # content = re.sub(r"http\S+", "", content)
        # content = content.replace('RT ', ' ').replace('&amp;', 'and')
        # content = re.sub('[^A-Za-z0-9]+', ' ', content)
        # content = content.lower()
        #
        # tokenized_word = word_tokenize(content)
        # stop_words = set(stopwords.words("english"))
        # filtered_sent = []
        # for w in tokenized_word:
        #     if w not in stop_words:
        #         filtered_sent.append(w)
        # fdist = FreqDist(filtered_sent)
        # fd = pd.DataFrame(fdist.most_common(10), columns=["Word", "Frequency"]).drop([0]).reindex()
        #
        # # Plot Bar chart
        # bar = go.Figure()
        #
        # bar.add_trace(
        #     go.Bar(x=fd["Word"],
        #            y=fd["Frequency"],
        #            name="Freq Dist"))
        #
        # bar.update_traces(marker_color='rgb(59, 89, 152)', marker_line_color='rgb(8,48,107)', \
        #                   marker_line_width=0.5, opacity=0.7)
        # bar.update_layout(title_text="Top 9 appeared words in live tweets", title_font_size=20)

        '''
        Plot
        the
        Geo - Distribution
        '''
        is_in_US=[]
        geo = df[['user_location']]
        df = df.fillna(" ")
        for x in df['user_location']:
            check = False
            for s in STATES:
                if s in x:
                    is_in_US.append(STATE_DICT[s] if s in STATE_DICT else s)
                    check = True
                    break
            if not check:
                is_in_US.append(None)

        geo_dist = pd.DataFrame(is_in_US, columns=['State']).dropna().reset_index()
        geo_dist = geo_dist.groupby('State').count().rename(columns={"index": "Number"}) \
                .sort_values(by=['Number'], ascending=False).reset_index()
        geo_dist["Log Num"] = geo_dist["Number"].apply(lambda x: math.log(x, 2))


        geo_dist['Full State Name'] = geo_dist['State'].apply(lambda x: INV_STATE_DICT[x])
        geo_dist['text'] = geo_dist['Full State Name'] + '<br>' + 'Num: ' + geo_dist['Number'].astype(str)

        choropleth_map = go.Figure()
        choropleth_map.add_trace(go.Choropleth(
            locations=geo_dist['State'],
            z=geo_dist['Log Num'].astype(float),
            locationmode = 'USA-states',
            colorscale = "Blues",
            text=geo_dist['text'],
            showscale=False,
            geo='geo'
            ))

        choropleth_map.update_layout(
            title_text= "Real-time tracking '{}' mentions on Twitter {} UTC".format(settings.data_on_word[0], datetime.datetime.utcnow().strftime('%m-%d %H:%M')),
            geo = dict(
                scope='usa',
            ),
            # template="plotly_dark",
            margin=dict(r=20, t=50, b=50, l=20),
            # annotations=[
            #     go.layout.Annotation(
            #         text="Source: Twitter",
            #         showarrow=False,
            #         xref="paper",
            #         yref="paper",
            #         x=0,
            #         y=0)
            # ],
            showlegend=False,
            xaxis_rangeslider_visible=True
        )


        line_chart_JSON = json.dumps(line_chart, cls=plotly.utils.PlotlyJSONEncoder)
        # bar_chart_JSON = json.dumps(bar, cls=plotly.utils.PlotlyJSONEncoder)
        choropleth_map_JSON = json.dumps(choropleth_map, cls=plotly.utils.PlotlyJSONEncoder)
        # return line_chart_JSON, bar_chart_JSON, choropleth_map_JSON
        return line_chart_JSON, choropleth_map_JSON

