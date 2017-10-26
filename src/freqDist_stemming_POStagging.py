from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string

with open('dirty_result.json', encoding = 'utf-8', mode='r') as f:
    try:
        dataset = json.load(f)
        for i in range(len(dataset)):
            dataset[i]['question'] = BeautifulSoup(dataset[i]['question'], 'html.parser').get_text()
            for j in range(len(dataset[i]['answers'])):
                dataset[i]['answers'][j] = BeautifulSoup(dataset[i]['answers'][j], 'html.parser').get_text()

    except Exception as e:
        print(e)
contractions = ["n't", "'s", "s'", "'d", "'ll" , "'ve", "'re", "'m"] + [x for x in string.punctuation] + [ x for x in '0123456789']
stop_words = corpus.stopwords.words("english")
words = []
sentences = []

for post in dataset:
    for sent in sent_tokenize(post['question']):
        sentences.append(sent)
        for token in word_tokenize(sent):
            if len(token) > 1 and token.lower() not in stop_words and token not in contractions and not re.search("^[\W\d]+$", token):
                words.append(token.lower())
    for texts in post['answers']:
        for sent in sent_tokenize(texts):
            sentences.append(sent)
            for token in word_tokenize(sent):
                if len(token) > 1 and token.lower() not in stop_words and token not in contractions and not re.search("^[\W\d]+$", token):
                    words.append(token.lower())

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
for i in stemDist.most_common(20):
    print(i)

words_stemmed = []
with open('top 20 stemmed.txt', encoding="utf-8",mode='w') as f:
    for stemmedword in stemDist.most_common(20):
        f.write('\n%s\n' %'#######################################')
        f.write('stemmed word: %s\n' %str(stemmedword))
        f.write('%s\n' %'showing all unique tokens')
        f.write("\n")
        for word in words:
            if stemmedword[0] in word and word not in words_stemmed:
                for i in range(len(stemmedword[0])):
                    if stemmedword[0][i] != word[i]:
                        break
                    elif i == len(stemmedword[0][i])-1:
                        words_stemmed.append(word)
                        f.write("%s\n" % word)
    f.write('%s\n' %'#######################################')
postagged = []




with open('random 10 POStags.txt', encoding="utf-8",mode='w') as f:
    for i in range(10):
        f.write('\n%s\n' %'#######################################')
        r = random.random()*len(sentences)
        if len(sentences[int(r)])<2:
            r = random.random()*len(sentences)
        for w in pos_tag(word_tokenize(sentences[int(r)])):
            f.write("%s\n" % str(w))
    f.write('%s\n' %'#######################################')
