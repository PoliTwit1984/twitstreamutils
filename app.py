import streamlit as st
import matplotlib.pyplot as plt
import re
from nltk.corpus import stopwords
import nltk
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud, STOPWORDS
import tweepy
import string
import textwrap
import pandas as pd
import pyodbc
import altair as alt
import textwrap

#
# nltk.download("stopwords")
# nltk.download("punkt")


def clean_text(text):

    # convert to lower case
    cleaned_text = text
    # remove HTML tags
    html_pattern = re.compile("<.*?>")
    cleaned_text = re.sub(html_pattern, "", cleaned_text)
    # remove punctuations
    cleaned_text = cleaned_text.translate(
        str.maketrans("", "", string.punctuation))

    return cleaned_text.strip()


def remove_whitespace(text):

    return " ".join(text.split())


def makeitastring(wannabestring):
    convertedstring = ",".join(map(str, wannabestring))
    return convertedstring


auth = tweepy.OAuthHandler(st.secrets["consumer_key"],
                           st.secrets["consumer_secret"])

auth.set_access_token(st.secrets["access_token"],
                      st.secrets["access_token_secret"])

api = tweepy.API(auth)

client = tweepy.Client(bearer_token=st.secrets["bearer_token"])
client2 = tweepy.Client(bearer_token=st.secrets["bearer_token"])

password = st.secrets["password"]
username = st.secrets["username"]


def app():
    st.set_option('deprecation.showPyplotGlobalUse', False)

    morewords = [
        "moleg",
        "Missouri",
        "make",
        "whatever",
        "say",
        "self",
        "defense",
        "morning",
        "back",
        "stand",
        "says",
        "ground",
        "rt",
        "will",
        "one",
        "now",
        "im",
        "new",
        "mo",
        "dont",
        "u",
        "state",
        "rt",
        "'moleg",
        "rt '",
        "rt'",
        "moleg'"
        "amp",
        "a",
        "b",
        "s",
        "t",
        "z"

    ]

    STOPWORDS.update(morewords)
    stopwords_ls = list(set(stopwords.words("english")))
    stopwords_ls = [clean_text(word) for word in stopwords_ls]
    st.sidebar.title("Politwit1984 Twitter Tools")
    page = st.sidebar.selectbox(
        "Select Tool", ["Twitter User Information", "Twitter User Wordcloud", "Twitter User Liked Posts WordCloud", "Twitter Lists a User Belongs", "Twitter database tests", "Real time Biden Sentiment", "Real time WordCloud", "St. Louis Twitter Trends"])
    st.title("Politwit1984 Twitter Analytic Tools")

    driver = "{ODBC Driver 17 for SQL Server}"
    server_name = "twitpoli1984-sqlsrv"
    database_name = "mosenatetweets-db"
    server = "{server_name}.database.windows.net,1433".format(
        server_name=server_name)

    connection_string = textwrap.dedent(
        """
        Driver={driver};
        Server={server};
        Database={database};
        Uid={username};
        Pwd={password};
        Encrypt=yes;
        TrustServerCertificate=no;
        Connection Timeout=30;
    """.format(
            driver=driver,
            server=server,
            database=database_name,
            username=st.secrets['username'],
            password=st.secrets['password']
        )
    )

    cnxn: pyodbc.Connection = pyodbc.connect(connection_string)
    crsr: pyodbc.Cursor = cnxn.cursor()
    # crsr.execute('SELECT * FROM table_name')

    df = pd.read_sql_query('SELECT * FROM TWEET_ALL_UP', cnxn)

    if page == "Twitter User Information":
        st.header("Twitter Utilities - Get User Info")
        twitter_user = st.text_input(
            "Enter Twitter screenname to get information about Twitter user."
        )
        if twitter_user:
            user = api.get_user(screen_name=twitter_user)
            st.write("User Twitter screen name: ", user.screen_name)
            st.write("User Name: ", user.name)
            st.write("User Description: ", user.description)
            st.write("User location: ", user.location)
            st.write("User created on: ", user.created_at)
            st.write("User Tweets: ", user.statuses_count)
            st.write("User liked tweets: ", user.favourites_count)
            st.write("User followers count: ", user.followers_count)
            st.write("User following count: ", user.friends_count)
            st.write("User geo-enabled: ", user.geo_enabled)
            st.write("User Twitter ID: ", user.id)
            st.write("User list memberships: ", user.listed_count)

    elif page == "Twitter User Wordcloud":
        tweet_list = []
        st.header("Twitter Utilities - Get User Wordcloud")
        twitter_name = st.text_input(
            "Enter Twitter screen name to get wordcloud of user's recent posts")
        if twitter_name:
            tweets = api.user_timeline(screen_name=twitter_name)

            for tweet in tweets:
                st.write(tweet.text)
                tweet_clean_text = clean_text(tweet.text)
                words = word_tokenize(tweet_clean_text)
                wordsFiltered = []
                for w in words:
                    if w not in stopwords_ls:
                        wordsFiltered.append(w)
                        tweet_clean_text = str(wordsFiltered)
                        tweet_list.append(tweet_clean_text)
            data = makeitastring(tweet_list)
            st.set_option('deprecation.showPyplotGlobalUse', False)
            cloud = WordCloud(
                scale=3,
                max_words=100,
                colormap="RdYlGn",
                background_color="black",
                stopwords=STOPWORDS,
                collocations=True,
            ).generate_from_text(data)
            plt.figure(figsize=(10, 8))
            plt.imshow(cloud)
            plt.axis("off")
            plt.show()
            st.pyplot()

    elif page == "Twitter User Liked Posts WordCloud":
        liked_tweets = []
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.header("Twitter Utilities - Get user liked posts ")
        twitter_handle = st.text_input(
            "Enter Twitter screen name to get tweets liked by the user user and print WordCloud.")
        if twitter_handle:
            username = twitter_handle
            userinfo = api.get_user(screen_name=username)
            user_id = userinfo.id

            response = client.get_liked_tweets(id=user_id, max_results=100)

            tweets = response.data
            metadata = response.meta
            for tweet in tweets:

                tweet_text = tweet.text

                tweet_clean_text = clean_text(tweet_text)
                tweet_created_at = tweet.created_at
                liked_tweets.append(tweet_clean_text)

            if liked_tweets:
                st.write("Working...")
                data = makeitastring(liked_tweets)
                cloud = WordCloud(scale=3,
                                  max_words=125,
                                  colormap='RdYlGn',
                                  background_color='black',
                                  stopwords=STOPWORDS,
                                  collocations=True).generate_from_text(data)
                plt.figure(figsize=(10, 8))
                plt.imshow(cloud)
                plt.axis('off')
                plt.show()
                st.pyplot()

    elif page == "Twitter Lists a User Belongs":
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.header("Twitter Utilities - Get memberships")
        twitter_username = st.text_input(
            "Enter screen name to get list of Twitter list memberships.")
        if twitter_username:
            userinfo = api.get_user(screen_name=twitter_username)
            user_id = userinfo.id
            response = client.get_list_memberships(user_id)
            for x in response.data:
                st.write(x.name, ('https://twitter.com/i/lists/'+str(x.id)))

    elif page == "Twitter database tests":
        st.header("Twitter database analysis")

        st.bar_chart(df['tweet_source'].value_counts(),
                     use_container_width=True)

        st.bar_chart(df['tweet_reference_type'].value_counts(),
                     use_container_width=True)

        st.bar_chart(df[['tweet_user_following_count']],
                     use_container_width=True)

        st.bar_chart(df['tweet_sentiment_label'].value_counts(),
                     use_container_width=True)

        print('hi')

        # c = alt.Chart(df).mark_bar().encode(
        # alt.Y('tweet_source'),
        # alt.X('count(kind):Q')

        c = alt.Chart(df).mark_bar().encode(
            alt.Y('tweet_source'),
            alt.X('count(tweet_source):Q'))
        st.altair_chart(c, use_container_width=True)

        e = alt.Chart(df).mark_bar().encode(
            x='tweet_source',
            y='count()',
            color='tweet_sentiment_label').interactive()
        st.altair_chart(e, use_container_width=True)

        f = alt.Chart(df).mark_bar().encode(
            x=alt.X('tweet_source', sort='-y'),
            y='count()',
            color='tweet_sentiment_label'
        )
        st.altair_chart(f, use_container_width=True)

        g = alt.Chart(df).mark_circle(size=60).encode(
            x='tweet_user_following_count',
            y='tweet_user_followers_count',
            color='tweet_source',
            size='tweet_user_followers_count',
            tooltip=["tweet_username", "tweet_user_following_count",
                     "tweet_user_followers_count", 'tweet_source']
        ).interactive()

        st.altair_chart(g, use_container_width=True)

        k = df.tweet_sentiment_label.value_counts().plot(
            kind="bar", color="plum", figsize=(10, 3), colormap="pastel")
        st.altair_chart(k, use_container_width=True)

    elif page == "Real time Biden Sentiment":
        st.header("Real time Biden Sentiment")
        crsr.execute("SELECT COUNT(*) FROM realtimetest")
        total = crsr.fetchall()
        total_score = 0
        i = 0
        o = (int(makeitastring(total[0])))
        o = o - 10
        t = 1
        w = 0
        placeholder = st.empty()
        while i < 1:
            crsr.execute(
                "SELECT tweet_score FROM realtimetest ORDER BY tweet_created_at OFFSET "
                + str(o)
                + " ROWS FETCH NEXT 1 ROWS ONLY"
            )
            results = crsr.fetchall()
            score = results[0]
            score = makeitastring((score))
            score = float(score)
            total_score = total_score + score

            with placeholder.container():

                st.metric(label="Realtime Trump Twitter Sentiment (the lower the number the lower the sentiment).", value=(
                    total_score), delta=(score))

                st.metric(
                    label="Number of Tweets mentioning Trump since you started watching.", value=t)

                w = w + 1
                i = 0
                o = o + 1
                t = t+1

    elif page == "Real time WordCloud":
        st.header("Real time Biden WordCloud")

        crsr.execute("SELECT COUNT(*) FROM realtimetest")
        total = crsr.fetchall()

        tweet_list = []
        total_score = 0
        i = 0
        o = (int(makeitastring(total[0])))
        o = o - 10
        t = 1
        w = 0
        placeholder = st.empty()
        while i < 1:
            crsr.execute(
                "SELECT tweet_text FROM realtimetest ORDER BY tweet_created_at OFFSET "
                + str(o)
                + " ROWS FETCH NEXT 1 ROWS ONLY"
            )

            results2 = crsr.fetchall()
            tweet_text = results2[0]
            tweet_text = makeitastring(tweet_text)
            tweet_text = clean_text(tweet_text)
            tweet_list.append(tweet_text)
            data = makeitastring(tweet_list)

            if w == 50:
                w = 0
                tweet_list = tweet_list[40:50]

            with placeholder.container():
                cloud = WordCloud(
                    scale=3,
                    max_words=150,
                    colormap="RdYlGn",
                    background_color="black",
                    stopwords=STOPWORDS,
                    collocations=True,
                ).generate_from_text(data)
                plt.figure(figsize=(10, 8))
                plt.imshow(cloud)
                plt.axis("off")
                st.pyplot()

                w = w + 1
                i = 0
                o = o + 1
                t = t + 1
    elif page == "St. Louis Twitter Trends":
        trends = api.get_place_trends(id="23424977")
        for value in trends:
            for trend in value['trends']:
                st.write(trend['name'] + " has tweet volume of: " +
                         str(trend['tweet_volume']))


if __name__ == "__main__":
    app()
