import streamlit as st
import matplotlib.pyplot as plt
import re
from nltk.corpus import stopwords
import nltk
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud, STOPWORDS
import tweepy
import string

nltk.download("stopwords")
nltk.download("punkt")

def clean_text(text):

    # convert to lower case
    cleaned_text = text.lower()
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

tweet_list = []


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
        "moleg'",
    ]

    STOPWORDS.update(morewords)
    stopwords_ls = list(set(stopwords.words("english")))
    stopwords_ls = [clean_text(word) for word in stopwords_ls]
    st.sidebar.title("Politwit1984 Twitter Tools")
    page = st.sidebar.selectbox(
        "Select Tool", ["Twitter User Information", "Twitter User Wordcloud", "Twitter User Liked Posts WordCloud", "Twitter Lists a User Belongs"])
    st.title("Politwit1984 Twitter Analytic Tools")

    if page == "Twitter User Information":
        st.header("Twitter Utilities - Get User Info")
        twitter_user = st.text_input(
            "Enter Twitter screen name to get information about Twitter user."
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
        st.header("Twitter Utilities - Get User Wordcloud")
        twitter_name = st.text_input(
            "Enter Twitter screen name to get wordcloud of user's recent posts.")
        if twitter_name:
            tweets = api.user_timeline(screen_name=twitter_name)
            for tweet in tweets:
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
                max_words=150,
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

                tweet_clean_text = clean_text(tweet.text)
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


if __name__ == "__main__":
    app()