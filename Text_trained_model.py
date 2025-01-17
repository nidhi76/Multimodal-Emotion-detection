# -*- coding: utf-8 -*-
"""Linux_text.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uyv_zBYp0VY7d8v4qdsCFaQ3LsKVVVMW
"""

import pandas as pd
import numpy as np

# text preprocessing
from nltk.tokenize import word_tokenize
import re

# plots and metrics
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

# preparing input to our model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical

# keras layers
from keras.models import Sequential
from keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense

import nltk
nltk.download('punkt')

# Number of labels: joy, anger, fear, sadness, neutral
num_classes = 5

# Number of dimensions for word embedding
embed_num_dims = 300

# Max input length (max number of words) 
max_seq_len = 500

class_names = ['happy', 'fear', 'angry', 'sad', 'neutral']

data_train = pd.read_csv("data_train.csv", encoding='utf-8')
data_test = pd.read_csv("data_test.csv", encoding='utf-8')

X_train = data_train.Text
X_test = data_test.Text

y_train = data_train.Emotion
y_test = data_test.Emotion

data = data_train.append(data_test, ignore_index=True)
#print(type(data.Text[0]))
#print(data.Emotion.value_counts())
#data.head(6)

def clean_text(data):
    
    # remove hashtags and @usernames
    data = re.sub(r"(#[\d\w\.]+)", '', data)
    data = re.sub(r"(@[\d\w\.]+)", '', data)
    import pandas as pd

    # tokenization using nltk
    data = word_tokenize(data)
    
    return data

texts = [' '.join(clean_text(text)) for text in data.Text]
print(texts)
texts_train = [' '.join(clean_text(text)) for text in X_train]
texts_test = [' '.join(clean_text(text)) for text in X_test]

print(texts_train[92])

tokenizer = Tokenizer()
print(tokenizer)
'''fit_on_texts Updates internal vocabulary based on a list of texts. This method creates the vocabulary index based on word frequency.
So if you give it something like, "The cat sat on the mat." It will create a dictionary s.t. word_index["the"] = 1; word_index["cat"] = 2 
it is word -> index dictionary so every word gets a unique integer value.
 0 is reserved for padding. So lower integer means more frequent word (often the first few are stop words because they appear a lot).'''
tokenizer.fit_on_texts(texts)
print(tokenizer)

'''texts_to_sequences Transforms each text in texts to a sequence of integers. So it basically takes each word in the text and replaces it
 with its corresponding integer value from the word_index dictionary '''
sequence_train = tokenizer.texts_to_sequences(texts_train)
print(sequence_train)
sequence_test = tokenizer.texts_to_sequences(texts_test)

index_of_words = tokenizer.word_index
print(index_of_words)

# vocab size is number of unique words + 0 index reserved for padding
vocab_size = len(index_of_words) + 1

print('Number of unique words: {}'.format(len(index_of_words)))

X_train_pad = pad_sequences(sequence_train, maxlen = max_seq_len )
X_test_pad = pad_sequences(sequence_test, maxlen = max_seq_len )

print(X_train_pad.shape)
print(X_test_pad.shape)
X_train_pad

encoding = {
    'happy': 0,
    'fear': 1,
    'angry': 2,
    'sad': 3,
    'neutral': 4
}

# Integer labels
y_train = [encoding[x] for x in data_train.Emotion]
print(y_train)
y_test = [encoding[x] for x in data_test.Emotion]

y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

y_train

word_embedding = np.load("embedd_matrix.npy")
print(word_embedding)
word_embedding.shape

# Inspect unseen words
new_words = 0

for word in index_of_words:
    entry = word_embedding[index_of_words[word]]
    if all(v == 0 for v in entry):
        new_words = new_words + 1

print('Words found in wiki vocab: ' + str(len(index_of_words) - new_words))
print('New words found: ' + str(new_words))

# Embedding layer before the actaul BLSTM 
embedd_layer = Embedding(vocab_size,
                         embed_num_dims,
                         input_length = max_seq_len,
                         weights = [word_embedding],
                         trainable=False)

# Convolution
kernel_size = 3
filters = 256

model = Sequential()
model.add(embedd_layer)
model.add(Conv1D(filters, kernel_size, activation='relu'))
model.add(GlobalMaxPooling1D())
model.add(Dense(256, activation='relu'))
model.add(Dense(num_classes, activation='softmax'))

model.load_weights('text_cnn_model.h5')

import time

message = input("Enter sentence : ")
msg =[]
msg.append(message)
seq = tokenizer.texts_to_sequences(msg)
padded = pad_sequences(seq, maxlen=max_seq_len)

start_time = time.time()
pred = model.predict(padded)

print('Message: ' + str(msg))
print('predicted: {} ({:.2f} seconds)'.format(class_names[np.argmax(pred)], (time.time() - start_time)))

