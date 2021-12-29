import streamlit as st
import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.title("Song Recommender")
st.header("Feeling sad? Feeling angry? Feeling Euphoric?")
st.subheader("Input the lyrics to a song you want to feel like and we'll give you some similar songs.")
st.image('images/faces.jpg')

genre = st.radio(
    "Do you want similar or happier songs?",
    ('Similar', 'Happier'))
if genre == 'Song Lyrics':
    st.write('Please include the full songs lyrics.')
    artist, song = st.text_input('Artist Name Here;'), st.text_input('Song Name Here;')

lyrics = st.text_area('Input Lyrics for the song here, or just write down how you want to feel.', '''No, no
I ain't ever trapped out the bando
But oh Lord, don't get me wrong, (...)
''')

small_data = pd.read_pickle('data/vadered&no_lyrics.pkl', compression={'method':'zip'})


def song_recs (sentence):
  
    my_tokenizer = RegexpTokenizer("[\w']+|\$[\d\.]+")
    clean_words = my_tokenizer.tokenize(sentence.lower())
    cleaned_sentence =  ' '.join(clean_words)
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(cleaned_sentence)
    mask= (small_data["vader_valence"]>(sentiment_dict['compound']))
    recs = small_data[mask].sort_values(by="vader_valence")[:10]
    return (recs[["artist", "song"]].set_index('artist', drop=True), sentiment_dict)

def happy_song_recs (sentence):
    my_tokenizer = RegexpTokenizer("[\w']+|\$[\d\.]+")
    clean_words = my_tokenizer.tokenize(sentence.lower())
    cleaned_sentence =  ' '.join(clean_words)
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(cleaned_sentence)
    mask= (small_data["vader_valence"]>(sentiment_dict['compound']+.3))
    recs = small_data[mask].sort_values(by="vader_valence")[:10]
    if sentiment_dict['compound'] +.3 > small_data["vader_valence"].max():
        return (small_data.sort_values(by="vader_valence").drop(columns = 'vader_valence')[-10:], sentiment_dict)
    return (recs[["artist", "song"]].set_index('artist', drop=True), sentiment_dict)

if genre == 'Similar':
    st.write('Try listening to one of these:', song_recs(lyrics)[0])

    st.write('The input had a sentiment score of', song_recs(lyrics)[1]['compound'])
    st.write('Sentiment score is a score derived from the lyrics of a song which scores it from positive:(.5+), neutral:(.5 to -5), and negative:(-.5 and below).')
else:
    if happy_song_recs(lyrics)[1]['compound']+.3 > small_data["vader_valence"].max():
        st.write('Try listening to one of these:', small_data.sort_values(by="vader_valence")[-1000:].sample(10).drop(columns='vader_valence').set_index('artist', drop=True))
    else:
        st.write('Try listening to one of these:', happy_song_recs(lyrics)[0])

    st.write('The input had a sentiment score  of', song_recs(lyrics)[1]['compound'])
    st.write('Sentiment score is a score derived from the lyrics of a song which scores it from positive:(.5+), neutral:(.5 to -5), and negative:(-.5 and below).')

