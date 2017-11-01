from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string
import time
import copy

##        Regex expressions##################################
methodpattern = [(r"(?:\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))",'METHOD')]
stringpattern = [(r"(?:(?<!\w)|r)(?:(?:\"{3}.+?\"{3})|(?:'{3}.+?'{3})|(?:\"(?:(?!\\n)[^\"])+?\")|(?:'(?:(?!\\n)[^'])+?'))(?!\w)",'STRING')]
commentpattern = [(r"(?:#[^#\n] *?(?!\\n|\n)[\S].+?)(?=\\n|\n)",'COMMENT')]
variablepattern = [(r'(?:(?<=\s)|^)(?:(?:[a-zA-Z_])(?:\.\w|\w)*?(?= *=)|(?:[a-zA-Z_])(?:\.\w|\w)*?(?=(?: *, *[a-zA-Z_][\w\.]*?)+(?= *=)))','VARIABLE')]
URLpattern = [(r'(?:(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w \.-]*)*\/?)','URL')]

POS_patterns = [(r"(?:\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))",'METHOD'),
                (r"(?:(?<!\w)|r)(?:(?:\"{3}.+?\"{3})|(?:'{3}.+?'{3})|(?:\"(?:(?!\\n)[^\"])+?\")|(?:'(?:(?!\\n)[^'])+?'))(?!\w)",'STRING'),
                (r"(?:#[^#\n] *?(?!\\n|\n)[\S].+?)(?=\\n|\n)",'COMMENT'),
                (r'(?:(?<=\s)|^)(?:(?:[a-zA-Z_])(?:\.\w|\w)*?(?= *=)|(?:[a-zA-Z_])(?:\.\w|\w)*?(?=(?: *, *[a-zA-Z_][\w\.]*?)+(?= *=)))','VARIABLE'),
                (r'(?:(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w \.-]*)*\/?)','URL')]

pattern = POS_patterns[0][0]+'|'+POS_patterns[1][0]+'|'+POS_patterns[2][0]+'|'+POS_patterns[3][0]+'|'+POS_patterns[4][0]
##############################################################



################ formatting datasets#############################
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


newdataset = copy.deepcopy(dataset)
dataset_IR = copy.deepcopy(newdataset)

######################################################################

#########             preparing variables     ########################
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
URLs = []
i = 0

print('time taken to prepare dataset: %f' %(time.time()-start))

########################################################################




##############       tokenize dataset                  ##############

## remove tokenized data from the dataset so that word_tokenize() will not duplicate existing tokens
start = time.time()
for i in range(len(dataset)):
##    print(i)
    sentences = sent_tokenize(dataset[i]['question'])
    for k in range(len(sentences)):
        tokens = regexp_tokenize(sentences[k], methodpattern[0][0])
        for l in range(len(tokens)):
            methods.append(tokens[l].lower())
            newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')
        tokens = regexp_tokenize(sentences[k], stringpattern[0][0])
        for l in range(len(tokens)):
            strings.append(tokens[l].lower())
            newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')
        tokens = regexp_tokenize(sentences[k], commentpattern[0][0])
        for l in range(len(tokens)):
            comments.append(re.sub('\s+?$', '', tokens[l].lower()))
            newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')
        tokens = regexp_tokenize(sentences[k], variablepattern[0][0])
        for l in range(len(tokens)):
            variables.append(tokens[l].lower())
##            newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')
        tokens = regexp_tokenize(sentences[k], URLpattern[0][0])
        for l in range(len(tokens)):
            URLs.append(tokens[l].lower())
            newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')
    for j in range(len(dataset[i]['answers'])):
        sentences = sent_tokenize(dataset[i]['answers'][j])
        for k in range(len(sentences)):
            tokens = regexp_tokenize(sentences[k], methodpattern[0][0])
            for l in range(len(tokens)):
                methods.append(tokens[l].lower())
                newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')
            tokens = regexp_tokenize(sentences[k], stringpattern[0][0])
            for l in range(len(tokens)):
                strings.append(tokens[l].lower())
                newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')
            tokens = regexp_tokenize(sentences[k], commentpattern[0][0])
            for l in range(len(tokens)):
                comments.append(re.sub('\s+?$', '', tokens[l].lower()))
                newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')
            tokens = regexp_tokenize(sentences[k], variablepattern[0][0])
            for l in range(len(tokens)):
                variables.append(tokens[l].lower())
##                newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')
            tokens = regexp_tokenize(sentences[k], URLpattern[0][0])
            for l in range(len(tokens)):
                URLs.append(tokens[l].lower())
                newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')



##          using word_tokenize() on english words
for post in newdataset:
    for sent in sent_tokenize(post['question']):
        for token in word_tokenize(sent.lower()):
            if len(token) > 1 and token.lower() not in stop_words and token not in contractions and not re.search("^[\W\d]+$", token) and token not in variables:
                mywords.append(token.lower())
    for texts in post['answers']:
        for sent in sent_tokenize(texts):
            sentences.append(sent.lower())
            for token in word_tokenize(sent):
                if len(token) > 1 and token.lower() not in stop_words and token not in contractions and not re.search("^[\W\d]+$", token) and token not in variables:
                    mywords.append(token.lower())

########################################################################



textDist = FreqDist(methods+strings+comments+URLs+variables+mywords)
print('time taken to tokenize: %f' %(time.time()-start))

##for i in sorted(set(comments)):
##    print(i)
##    print('========')

##print("\n Top 20 words")
##for i in textDist.most_common(20):
##    print(i)



#########           checking for irregular words        ####################

irregularWords = []
print('there are ' + str(len(mywords)) + ' english words.')
start = time.time()
i = len(mywords)
for token in mywords:
    if i % 100000 == 0:
        print(i)
    i-=1
    if token not in stop_words and token not in contractions:
        lemmaed_token = lmtzr.lemmatize(token)
        stemmed_token = ps.stem(token)
        lemmaedV_token = lmtzr.lemmatize(token, 'v')
        if lemmaed_token not in mydict and lemmaedV_token not in mydict and stemmed_token not in mydict:
            irregularWords.append(token)
print('time taken to check for irregulars: %f' %(time.time()-start))

########################################################################




###################       create top20 irregular words text file      ####################

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
                if re.match(re.escape(irregularWord[0]),word):
                    top20irregulars.append(word)
                    f.write("%s\n" % word)
    f.write('%s\n' %'#######################################')

print('time taken to consolidate irregulars: %f' %(time.time()-start))

############################################################################################




###############             tokenize dataset into sentences               ####################

start = time.time()
sentences = []
for i in range(len(dataset_IR)):
    p=0
    j=0
    while j < len(dataset_IR[i]['question']):
        if dataset_IR[i]['question'][j] == '\n':
            if dataset_IR[i]['question'][j-1] in contractions:
                if not (re.search(pattern,dataset_IR[i]['question'][p:j])):
                    dataset_IR[i]['question'] = dataset_IR[i]['question'][:j]+'. '+dataset_IR[i]['question'][j+1:]

            p = j
        j+=1

    for k in range(len(dataset_IR[i]['answers'])):
        p=0
        j=0
        while j < len(dataset_IR[i]['answers'][k]):
            if dataset_IR[i]['answers'][k][j] == '\n':
                if dataset_IR[i]['answers'][k][j-1] in contractions:
                    if not (re.search(pattern,dataset_IR[i]['answers'][k][p:j])):
                        dataset_IR[i]['answers'][k] = dataset_IR[i]['answers'][k][:j] + '. ' + dataset_IR[i]['answers'][k][j+1:]

                p = j
            j+=1


    for sent in sent_tokenize(dataset_IR[i]['question']):
        if not re.search(pattern, sent):
            sent=sent[:-1]
        if len(sent)>2:
            sentences.append(sent.lower())
    for texts in dataset_IR[i]['answers']:
        for sent in sent_tokenize(texts):
            if not re.search(pattern, sent):
                sent=sent[:-1]
            if len(sent)>2:
                sentences.append(sent.lower())

print('time taken to prepare dataset_IR: %f' %(time.time()-start))
########################################################################





##############                consolidate all sentences containing irregular words         ###############
######################                      takes 50 minutes                      ########################

start = time.time()
print('there are '+str(len(set(sentences))*len(set(irregularWords)))+' comparisons to make')
i=len(set(sentences))*len(set(irregularWords))
irregularWordSentence = []
IR_sents = []
for word in set(irregularWords):
    for sent in set(sentences):
        if i % 1000000 == 0:
            print(i)
        i-=1
        wordpattern = '\W'+re.escape(word)+'\W'
        if re.search(wordpattern, sent) and sent not in set(IR_sents) and len(sent)>3:
            irregularWordSentence.append([(word,sent),sent])
            IR_sents.append(sent)

print('time taken to check irregulars sentences: %f' %(time.time()-start))



########################################################################



################          write random_10_POStags_with_irregulars file               ####################
with open('random_10_POStags_with_irregulars.txt', encoding="utf-8",mode='w') as f:
    for i in range(10):
        r = int(random.random()*len(irregularWordSentence))
        f.write('\n%s\n' %'#######################################')
        f.write("%s\n\n" % ('irregular word: '+str(irregularWordSentence[int(r)][0])))
        tokens = list(set(regexp_tokenize(irregularWordSentence[int(r)][1], pattern)))
        for l in range(len(tokens)):
            if len(tokens[l])>3:
                irregularWordSentence[int(r)][1] = irregularWordSentence[int(r)][1].replace(tokens[l],'')
        for token in word_tokenize(irregularWordSentence[int(r)][1]):
            if token not in tokens:
                tokens.append(token)
        for w in pythontagger.tag(tokens):
            f.write("%s\n" % str(w))
    f.write('%s\n' %'#######################################')

########################################################################
