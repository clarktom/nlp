from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string
import time

methodpattern = [(r"(?:\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))",'METHOD')]
stringpattern = [(r"(?:(?<!\w)|r)(?:(?:\"{3}.+?\"{3})|(?:'{3}.+?'{3})|(?:\"(?:(?!\\n)[^\"])+?\")|(?:'(?:(?!\\n)[^'])+?'))(?!\w)",'STRING')]
commentpattern = [(r"(?:#[^#\n] *?(?!\\n|\n)[\S].+?)(?=\\n|\n)",'COMMENT')]
variablepattern = [(r'(?:(?<=\s)|^)(?:(?:[a-zA-Z_])(?:\.\w|\w)*?(?= *=)|(?:[a-zA-Z_])(?:\.\w|\w)*?(?=(?: *, *[a-zA-Z_][\w\.]*?)+(?= *=)))','VARIABLE')]

POS_patterns = [(r"(?:\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))",'METHOD'),
                (r"(?:(?<!\w)|r)(?:(?:\"{3}.+?\"{3})|(?:'{3}.+?'{3})|(?:\"(?:(?!\\n)[^\"])+?\")|(?:'(?:(?!\\n)[^'])+?'))(?!\w)",'STRING'),
                (r"(?:#[^#\n] *?(?!\\n|\n)[\S].+?)(?=\\n|\n)",'COMMENT'),
                (r'(?:(?<=\s)|^)(?:(?:[a-zA-Z_])(?:\.\w|\w)*?(?= *=)|(?:[a-zA-Z_])(?:\.\w|\w)*?(?=(?: *, *[a-zA-Z_][\w\.]*?)+(?= *=)))','VARIABLE')]

pattern = POS_patterns[0][0]+'|'+POS_patterns[1][0]+'|'+POS_patterns[2][0]+'|'+POS_patterns[3][0]

start = time.time()
with open('dirty_result.json', encoding = 'utf-8', mode='r') as f:
    try:
        dataset = json.load(f)
        for i in range(len(dataset)):
            dataset[i]['question'] = BeautifulSoup(dataset[i]['question'], 'html.parser').get_text()
            for j in range(len(dataset[i]['answers'])):
                dataset[i]['answers'][j] = BeautifulSoup(dataset[i]['answers'][j], 'html.parser').get_text()
    except Exception as e:
        print(e)
with open('dirty_result.json', encoding = 'utf-8', mode='r') as f:
    try:
        newdataset = json.load(f)
        for i in range(len(dataset)):
            newdataset[i]['question'] = BeautifulSoup(newdataset[i]['question'], 'html.parser').get_text()
            for j in range(len(dataset[i]['answers'])):
                newdataset[i]['answers'][j] = BeautifulSoup(newdataset[i]['answers'][j], 'html.parser').get_text()
    except Exception as e:
        print(e)
with open('dirty_result.json', encoding = 'utf-8', mode='r') as f:
    try:
        dataset_IR = json.load(f)
        for i in range(len(dataset)):
            dataset_IR[i]['question'] = BeautifulSoup(dataset_IR[i]['question'], 'html.parser').get_text()
            for j in range(len(dataset[i]['answers'])):
                dataset_IR[i]['answers'][j] = BeautifulSoup(dataset_IR[i]['answers'][j], 'html.parser').get_text()
    except Exception as e:
        print(e)
stop_words = set(corpus.stopwords.words("english"))
contractions = set(["n't", "'s", "s'", "'d", "'ll" , "'ve", "'re", "'m"] + [x for x in string.punctuation] + [ x for x in '0123456789'])
mydict = set([x.lower() for x in corpus.words.words()])
ps = stem.PorterStemmer()
lmtzr = stem.wordnet.WordNetLemmatizer()
tagger_path = r'english.pickle'
default_tagger = data.load(tagger_path)
pythontagger = RegexpTagger(POS_patterns, backoff = default_tagger)

methods = []
strings = []
comments = []
variables = []
mywords = []
newdataset = dataset
dataset_IR = dataset[:]
i = 0

print('time taken to prepare dataset: %f' %(time.time()-start))

start = time.time()
for i in range(len(dataset)):
##    print(i)
    sentences = sent_tokenize(dataset[i]['question'])
    for k in range(len(sentences)):
        tokens = regexp_tokenize(sentences[k], methodpattern[0][0])
        for l in range(len(tokens)):
            methods.append(tokens[l].lower())
            newdataset[i]['question'] = dataset[i]['question'].replace(tokens[l],'')
        tokens = regexp_tokenize(sentences[k], stringpattern[0][0])
        for l in range(len(tokens)):
            strings.append(tokens[l].lower())
            newdataset[i]['question'] = dataset[i]['question'].replace(tokens[l],'')
        tokens = regexp_tokenize(sentences[k], commentpattern[0][0])
        for l in range(len(tokens)):
            comments.append(re.sub('\s+?$', '', tokens[l].lower()))
            newdataset[i]['question'] = dataset[i]['question'].replace(tokens[l],'')
        tokens = regexp_tokenize(sentences[k], variablepattern[0][0])
        for l in range(len(tokens)):
            variables.append(tokens[l].lower())
            newdataset[i]['question'] = dataset[i]['question'].replace(tokens[l],'')
    for j in range(len(dataset[i]['answers'])):
        sentences = sent_tokenize(dataset[i]['answers'][j])
        for k in range(len(sentences)):
            tokens = regexp_tokenize(sentences[k], methodpattern[0][0])
            for l in range(len(tokens)):
                methods.append(tokens[l].lower())
                newdataset[i]['answers'][j] = dataset[i]['answers'][j].replace(tokens[l],'')
            tokens = regexp_tokenize(sentences[k], stringpattern[0][0])
            for l in range(len(tokens)):
                strings.append(tokens[l].lower())
                newdataset[i]['answers'][j] = dataset[i]['answers'][j].replace(tokens[l],'')
            tokens = regexp_tokenize(sentences[k], commentpattern[0][0])
            for l in range(len(tokens)):
                comments.append(re.sub('\s+?$', '', tokens[l].lower()))
                newdataset[i]['answers'][j] = dataset[i]['answers'][j].replace(tokens[l],'')
            tokens = regexp_tokenize(sentences[k], variablepattern[0][0])
            for l in range(len(tokens)):
                variables.append(tokens[l].lower())
                newdataset[i]['answers'][j] = dataset[i]['answers'][j].replace(tokens[l],'')


for post in newdataset:
    for sent in sent_tokenize(post['question']):
        for token in word_tokenize(sent.lower()):
            if len(token) > 1 and token.lower() not in stop_words and token not in contractions and not re.search("^[\W\d]+$", token):
                mywords.append(token.lower())
    for texts in post['answers']:
        for sent in sent_tokenize(texts):
            sentences.append(sent.lower())
            for token in word_tokenize(sent):
                if len(token) > 1 and token.lower() not in stop_words and token not in contractions and not re.search("^[\W\d]+$", token):
                    mywords.append(token.lower())

textDist = FreqDist(methods+strings+comments+mywords)
print('time taken to tokenize: %f' %(time.time()-start))

##for i in sorted(set(comments)):
##    print(i)
##    print('========')

##print("\n Top 20 words")
##for i in textDist.most_common(20):
##    print(i)

def binarySearch(word, array):
    start, end = 0, (len(array) - 1)
    while start <= end:
        mid = (start + end) // 2
        if word in array[mid]:
            return (True,array[mid])
        if word < array[mid]:
            end = mid - 1
        else:  # elem > arr[mid]
            start = mid + 1

    return (False,None)


irregularWords = []

print('there are ' + str(len(mywords)) + ' english words.')
start = time.time()
i = len(mywords)
for token in mywords:
    if i % 10000 == 0:
        print(i)
    i-=1
##    search = binarySearch(token, sorted(set(irregularWords)))
##    if search[0]:
####        print('yay')
##        irregularWords.append(search[1])
##        continue
    if token not in stop_words and token not in contractions:
        lemmaed_token = lmtzr.lemmatize(token)
        stemmed_token = ps.stem(token)
        lemmaedV_token = lmtzr.lemmatize(token, 'v')
        if lemmaed_token not in mydict and lemmaedV_token not in mydict and stemmed_token not in mydict:
            irregularWords.append(token)
print('time taken to check for irregulars: %f' %(time.time()-start))

irregularWordsDist = FreqDist(irregularWords)
##print("\n Top 20 irregular words")
start = time.time()
top20irregulars = []
with open('top_20_irregulars.txt', encoding="utf-8",mode='w') as f:
    for irregularWord in irregularWordsDist.most_common(20):
##        print(irregularWord)
        f.write('\n%s\n' %'#######################################')
        f.write('irregular word: %s\n' %str(irregularWord))
        f.write('%s\n' %'showing all unique tokens')
        f.write("\n")
        for word in irregularWords:
            if irregularWord[0] in word and word not in set(top20irregulars):
                if re.match(irregularWord[0],word):
                    top20irregulars.append(word)
                    f.write("%s\n" % word)
##                for i in range(len(irregularWord[0])):
##                    if irregularWord[0][i] != word[i]:
##                        break
##                    elif i == len(irregularWord[0][i])-1:
##                        top20irregulars.append(word)
##                        f.write("%s\n" % word)
    f.write('%s\n' %'#######################################')

print('time taken to consolidate irregulars: %f' %(time.time()-start))
##for i in range(len(dataset_IR)):
##    dataset_IR[i]['question'] = dataset_IR[i]['question'].replace(r'\n', '. ')
##    for j in range(len(dataset[i]['answers'])):
##        dataset_IR[i]['answers'][j] = dataset_IR[i]['answers'][j].replace(r'\n', '. ')
sentences = []
for post in dataset_IR:
    sentences_with_newline = [sent.split('\n') for sent in sent_tokenize(post['question'])]
    for sentence in sentences_with_newline:
        for sent in sentence:
            if len(sent)>2:
                sentences.append(sent.lower())
    for texts in post['answers']:
        sentences_with_newline = [sent.split('\n') for sent in sent_tokenize(texts)]
        for sentence in sentences_with_newline:
            for sent in sentence:
                if len(sent)>2:
                    sentences.append(sent.lower())
start = time.time()
print('there are '+str(len(set(sentences))*len(set(irregularWords)))+' comparisons to make')
i=len(set(sentences))*len(set(irregularWords))
irregularWordSentence = []
IR_sents = []
for word in set(irregularWords):
    for sent in set(sentences):
        if i % 100000 == 0:
            print(i)
        i-=1
        wordpattern = '\W'+re.escape(word)+'\W'
        if re.search(wordpattern, sent) and sent not in set(IR_sents) and len(sent)>3:
            irregularWordSentence.append([(word,sent),sent])
            IR_sents.append(sent)

print('time taken to check irregulars sentences: %f' %(time.time()-start))

with open('random_10_POStags_with_irregulars.txt', encoding="utf-8",mode='w') as f:
    for i in range(10):
        r = int(random.random()*len(irregularWordSentence))
        f.write('\n%s\n' %'#######################################')
        f.write("%s\n\n" % ('irregular word: '+str(irregularWordSentence[int(r)][0])))
        tokens = regexp_tokenize(irregularWordSentence[int(r)][1], pattern)
        for l in range(len(tokens)):
            irregularWordSentence[int(r)][1] = irregularWordSentence[int(r)][1].replace(tokens[l],'')
        for token in word_tokenize(irregularWordSentence[int(r)][1]):
            tokens.append(token)
        for w in pythontagger.tag(tokens):
            f.write("%s\n" % str(w))
    f.write('%s\n' %'#######################################')

