from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string
import time
import pprint

# negationExpressionPattern = [(r"(?:[^.?!:\r\n]*(?:No|Not|Neither|Never|No one|Nobody|None|Nor|Nothing|Nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:no|not|neither|never|no one|nobody|none|nor|nothing|nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*(?:n(?:'|’)t|less)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:few|hardly|little|rarely|scarcely|seldom)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:de|dis|un)[^.?!:]*(?:\.|\?|!|:))",'NEGATION')]
# negationExpressionPattern = [(r"(?:[^.?!:\r\n]*(?:No|Not|Neither|Never|No one|Nobody|None|Nor|Nothing|Nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:no|not|neither|never|no one|nobody|none|nor|nothing|nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*(?:n(?:'|’)t|less)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:few|hardly|little|rarely|scarcely|seldom)\b[^.?!:]*(?:\.|\?|!|:))",'NEGATION')]
negationExpressionPattern = [(r"(?:[^.?!:\r\n]*(?:No|Not|Neither|Never|No one|Nobody|None|Nor|Nothing|Nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:no|not|neither|never|no one|nobody|none|nor|nothing|nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*(?:n(?:'|’)t)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:few|hardly|little|rarely|scarcely|seldom)\b[^.?!:]*(?:\.|\?|!|:))",'NEGATION')]

negationTagger = RegexpTagger(negationExpressionPattern)

with open('dirty_result.json', encoding = 'utf-8', mode='r') as f:
    try:
        dataset = json.load(f)
        for i in range(len(dataset)):
            dataset[i]['question'] = BeautifulSoup(dataset[i]['question'], 'html.parser').get_text()
            for j in range(len(dataset[i]['answers'])):
                dataset[i]['answers'][j] = BeautifulSoup(dataset[i]['answers'][j], 'html.parser').get_text()

    except Exception as e:
        print(e)

# pprint.pprint(dataset)
# exit(0)

stop_words = corpus.stopwords.words("english")
contractions = ["n't", "'s", "s'", "'d", "'ll" , "'ve", "'re", "'m"] + [x for x in string.punctuation] + [ x for x in '0123456789']
mydict = [x.lower() for x in corpus.words.words()]
ps = stem.PorterStemmer()
lmtzr = stem.wordnet.WordNetLemmatizer()

mywords = []
negations = []
newdataset = dataset
i = 0
for i in range(len(dataset)):
##    print(i)
    sentences = sent_tokenize(dataset[i]['question'])
    for k in range(len(sentences)):
        tokens = regexp_tokenize(sentences[k], negationExpressionPattern[0][0])
        for l in range(len(tokens)):
            negations.append(tokens[l].lower())
            newdataset[i]['question'] = dataset[i]['question'].replace(tokens[l],'')
            # print("dataset[i]['question']", dataset[i]['question'])
            # print("newdataset[i]['question']", newdataset[i]['question'])
    for j in range(len(dataset[i]['answers'])):
        sentences = sent_tokenize(dataset[i]['answers'][j])
        for k in range(len(sentences)):
            tokens = regexp_tokenize(sentences[k], negationExpressionPattern[0][0])
            # print(tokens)
            for l in range(len(tokens)):
                negations.append(tokens[l].lower())
                # print("i:", i)
                # print("j:", j)
                # print("l:", l)
                # print("newdataset:", len(newdataset))
                # print("newdataset[i]['answers']:", len(newdataset[i]['answers']))
                # print("dataset[i]['question']:", len(dataset[i]['question']))
                newdataset[i]['answers'][j] = dataset[i]['answers'][j].replace(tokens[l],'')

print("Negations:", negations)
pprint.pprint(negations)
