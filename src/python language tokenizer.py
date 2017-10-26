from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string

methodpattern = [(r"(?:\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))",'METHOD')]
stringpattern = [(r"(?:(?<!\w)|r)(?:(?:\"{3}.+?\"{3})|(?:'{3}.+?'{3})|(?:\"(?:(?!\\n)[^\"])+?\")|(?:'(?:(?!\\n)[^'])+?'))(?!\w)",'STRING')]
commentpattern = [(r"(?:#[^#\n] *?(?!\\n|\n)[\S].+?)(?=\\n|\n)",'COMMENT')]
variablepattern = [(r'(?:\b)((?:[a-zA-Z]|_)(?:(?:\.(?:_|\w)|(?:_|\w)))*\((?:.*)\))','VARIABLE')]

methodtagger = RegexpTagger(methodpattern)
stringtagger = RegexpTagger(stringpattern)
commenttagger = RegexpTagger(commentpattern)
variabletagger = RegexpTagger(variablepattern)


with open('dirty_result.json', encoding = 'utf-8', mode='r') as f:
    try:
        dataset = json.load(f)
        for i in range(len(dataset)):
            dataset[i]['question'] = BeautifulSoup(dataset[i]['question'], 'html.parser').get_text()
            for j in range(len(dataset[i]['answers'])):
                dataset[i]['answers'][j] = BeautifulSoup(dataset[i]['answers'][j], 'html.parser').get_text()

    except Exception as e:
        print(e)

stop_words = corpus.stopwords.words("english")
contractions = ["n't", "'s,", "s'", "'d", "'ll" , "'ve", "'re", "'m"]
mydict = [x.lower() for x in corpus.words.words()]
ps = stem.PorterStemmer()
lmtzr = stem.wordnet.WordNetLemmatizer()

methods = []
strings = []
comments = []
variables = []
mywords = []
newdataset = dataset
i = 0

for i in range(len(dataset)):
    print(i)
    sentences = sent_tokenize(dataset[i]['question'])
    for k in range(len(sentences)):
        tokens = regexp_tokenize(sentences[k], methodpattern[0][0])
        for l in range(len(tokens)):
            methods.append(tokens[l].lower)
            newdataset[i]['question'] = dataset[i]['question'].replace(tokens[l],'')
        tokens = regexp_tokenize(sentences[k], stringpattern[0][0])
        for l in range(len(tokens)):
            strings.append(tokens[l].lower())
            newdataset[i]['question'] = dataset[i]['question'].replace(tokens[l],'')
        tokens = regexp_tokenize(sentences[k], commentpattern[0][0])
        for l in range(len(tokens)):
            comments.append(re.sub('\s+?$', '', tokens[l].lower()))
            newdataset[i]['question'] = dataset[i]['question'].replace(tokens[l],'')
    for j in range(len(dataset[i]['answers'])):
        sentences = sent_tokenize(dataset[i]['answers'][j])
        for k in range(len(sentences)):
            tokens = regexp_tokenize(sentences[k], methodpattern[0][0])
            for l in range(len(tokens)):
                methods.append(tokens[l].lower())
                newdataset[i]['answers'][j] = dataset[i]['question'][j].replace(tokens[l],'')
            tokens = regexp_tokenize(sentences[k], stringpattern[0][0])
            for l in range(len(tokens)):
                strings.append(tokens[l].lower())
                newdataset[i]['answers'][j] = dataset[i]['question'][j].replace(tokens[l],'')
            tokens = regexp_tokenize(sentences[k], commentpattern[0][0])
            for l in range(len(tokens)):
                comments.append(re.sub('\s+?$', '', tokens[l].lower()))
                newdataset[i]['answers'][j] = dataset[i]['question'][j].replace(tokens[l],'')


for post in newdataset:
    for sent in sent_tokenize(post['question']):
        for token in word_tokenize(sent):
            if token.lower() not in stop_words and token not in contractions and token not in string.punctuation and not re.match("^[\W]+$", token):
                mywords.append(token.lower())
    for texts in post['answers']:
        for sent in sent_tokenize(texts):
            for token in word_tokenize(sent):
                if token.lower() not in stop_words and token not in contractions and token not in string.punctuation and not re.match("^[\W]+$", token):
                    mywords.append(token.lower())
                    
textDist = FreqDist(methods+strings+comments+mywords)

##for i in sorted(set(comments)):
##    print(i)
##    print('========')


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



