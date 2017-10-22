from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string

with open('../data/dirty_result.json', 'r') as f:
    try:
        dataset = json.load(f)

    except Exception as e:
        print(e)

stop_words = corpus.stopwords.words("english")
text = ""
words = []
sentences = []
##for post in dataset[:10]:
##    for texts in post['posts']:
##        text += BeautifulSoup(texts, 'html.parser').get_text()
##        text += ' '
for post in dataset[:50]:
    for texts in post['posts']:
        for sent in sent_tokenize(BeautifulSoup(texts, 'html.parser').get_text()):
            newstring = ''
            for e in sent:
                if e.isalpha():
                    newstring += e.lower()
                else:
                    newstring += ' '
            sentences.append(newstring)
            for token in word_tokenize(newstring):
                if token not in stop_words and token:
                    words.append(token)

textDist = FreqDist(words)

print("\n Top 20 words")
for i in textDist.most_common(20):
    print(i)


ps = stem.PorterStemmer()

stemmed = []

for w in words:
    stemmed.append(ps.stem(w))

stemDist = FreqDist(stemmed)

print("\n Top 20 stemmed")
for i in stemDist.most_common(24):
    print(i)

words_stemmed = []

for stemmedword in stemDist.most_common(20):
    print("")
    for word in words:
        if stemmedword[0] in word and word not in words_stemmed:
            for i in range(len(stemmedword[0])):
                if stemmedword[0][i] != word[i]:
                    break
                elif i == len(stemmedword[0][i])-1:
                    words_stemmed.append(word)
                    print(word)

postagged = []

##random = random.random()*len(sentences)
##for i in range(10):
##    for w in pos_tag(word_tokenize(sentences[int(random)])):
##        postagged.append(w)
##        print(w)
