import re
import string
import spacy
import pandas as pd
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
nlp = spacy.load("en_core_web_sm")
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import pickle

# Read csv file from system and creating dataframe and labelling it.
df = pd.read_csv("twitter_data.csv")
x = df["tweet"]
y = df['class']

label_encoder = LabelEncoder()
integer_encoded = label_encoder.fit_transform(y)
# Perform one-hot encoding
onehot_encoder = OneHotEncoder()
y_encoded = onehot_encoder.fit_transform(integer_encoded.reshape(-1, 1)).toarray()

stopword =list(STOP_WORDS)
punctuation = punctuation + '\n'
# # #Cleaning the data
def clean(text):
    text = str(text).lower()
    text = re.sub('\[.*?\]','',text)
    text = re.sub('https?://S+|www\.\S+','',text)
    text = re.sub('[%s]'% re.escape(string.punctuation),'',text)
    text = re.sub('\n','',text)
    text = re.sub('\w*\d\w*','', text)
    text = [word for word in text.split(' ') if word not in stopword]
    text = " ".join(text)
    return text

# # applying cleaning to the text
x_clean = x.apply(clean)

# # Fit and train the model using tweet data
cv = CountVectorizer()
x_trans = cv.fit_transform(x_clean)
x_train,x_test,y_train,y_test = train_test_split(x_trans , y_encoded , test_size=.33 , random_state= 42)
clf = DecisionTreeClassifier()
model = clf.fit(x_train,y_train)

pickle.dump((cv, model), open('model.pkl', 'wb'))

# Code for Summarizer

class Summarize:
    def __init__(self, test_data) -> None:
        self.test_data = test_data
        self.nlp = spacy.load('en_core_web_sm')
        self.doc = self.nlp(self.test_data)
        self.tokens = [token.text for token in self.doc]

    @staticmethod
    def word_freq_counter(doc):
        word_freq = {}
        stop_words = list(STOP_WORDS)
        for word in doc:
            if word.text.lower() not in stop_words and word.text.lower() not in punctuation:
                if word.text not in word_freq.keys():
                    word_freq[word.text] = 1
                else:
                    word_freq[word.text] += 1
        return word_freq

    @staticmethod
    def sentence_score(doc, word_freq):
        sent_score = {}
        sent_token = [sent for sent in doc.sents]
        for sent in sent_token:
            for word in sent:
                if word.text.lower() in word_freq.keys():
                    if sent not in sent_score.keys():
                        sent_score[sent] = word_freq[word.text.lower()]
                    else:
                        sent_score[sent] += word_freq[word.text.lower()]  
        return sent_score  

    def summarize_text(self):
        doc = self.nlp(self.test_data)
        word_freq = self.word_freq_counter(doc)
        max_freq = max(word_freq.values())
        for word in word_freq.keys():
            word_freq[word] = word_freq[word] / max_freq
        sent_score = self.sentence_score(doc, word_freq)
        return sent_score

 

