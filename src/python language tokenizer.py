from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string

methodpattern = [(r"(?:\\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))",'METHOD')]
stringpattern = [(r"(?<!\w)(?:(?:\"{3}(?:.|\n)+?\"{3})|(?:'{3}(?:.|\n)+?'{3})|(?:\"[^\"\n]*\w[^\"\n]*\")|(?:'[^'\n]*\w[^'\n]*'))(?!\w)",'STRING')]
commentpattern = [(r"(?:\\b)(?:#.+)",'COMMENT')]
variablepattern = [(r'(?:\\b)((?:[a-zA-Z]|_)(?:(?:\.(?:_|\w)|(?:_|\w)))*\((?:.*)\))','VARIABLE')]

methodtagger = RegexpTagger(methodpattern)
stringtagger = RegexpTagger(stringpattern)
commenttagger = RegexpTagger(commentpattern)
variabletagger = RegexpTagger(variablepattern)

stop_words = corpus.stopwords.words("english")

with open('dirty_result.json', encoding = 'utf-8', mode='r') as f:
    try:
        dataset = json.load(f)

    except Exception as e:
        print(e)

mydict = [x.lower() for x in corpus.words.words()]
ps = stem.PorterStemmer()
lmtzr = stem.wordnet.WordNetLemmatizer()

methods = []
strings = []
comments = []
variables = []
mywords = []
for post in dataset[5:10]:
    for texts in post['answers']:
        for sent in sent_tokenize(BeautifulSoup(texts, 'html.parser').get_text()):
##            for token in regexp_tokenize(sent, methodpattern[0][0]):
##                methods.append(token.lower())
##            for token in regexp_tokenize(sent, stringpattern[0][0]):
##                strings.append(token.lower())
            for token in regexp_tokenize(sent, "(?:\\b)(#.+[^\n])"):
                comments.append(token.lower())
##            for token in regexp_tokenize(sent, "(#.+)"):
##                variables.append(token.lower())
##    for texts in post['question']:
##        for sent in sent_tokenize(BeautifulSoup(texts, 'html.parser').get_text()):
##            for token in regexp_tokenize(sent, "(?:\\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))"):
##                methods.append(token.lower())
##            for token in regexp_tokenize(sent, "(?:\"[^\"\n]+\w[^\"\n]+\")|(?:'[^\"\n]+\w[^\"\n]+')|(?:\"{3}[^\"\n]+\w[^\"\n]+\"{3})|(?:'{3}[^'{3}]+'{3})"):
##                strings.append(token.lower())
##            for token in regexp_tokenize(sent, "(?:\\b)(?:#.+)"):
##                comments.append(token.lower())
##            for token in regexp_tokenize(sent, "(#.+)"):
##                variables.append(token.lower())
textDist = FreqDist(mywords)

for i in (set(comments)):
    print(i)
    print('========')


print("\n Top 20 words")
for i in textDist.most_common(20):
    print(i)

postagged = []

##print("\npostagged:")
for w in pos_tag(mywords):
    postagged.append(w)
##    print(w)

##irregulars = []
##for token in mywords:
##    lemmaed_token = lmtzr.lemmatize(token.lower())
##    stemmed_token = ps.stem(token.lower())
##    lemmaedV_token = lmtzr.lemmatize(token.lower(), 'v')
####    token = newtoken
##    if token.lower() not in stop_words and lemmaed_token not in mydict and lemmaedV_token not in mydict and stemmed_token not in mydict:
##        irregulars.append(token.lower())
##irregularsDist = FreqDist(irregulars)



