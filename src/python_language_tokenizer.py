from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string
import time
import copy

##        Regex expressions##################################
methodpattern = (r"(?:\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))",'METHOD')
stringpattern = (r"(?:(?<!\w)|r)(?:(?:\"{3}.+?\"{3})|(?:'{3}.+?'{3})|(?:\"(?:(?!\\n)[^\"])+?\")|(?:'(?:(?!\\n)[^'])+?'))(?!\w)",'STRING')
commentpattern = (r"(?:#[^#\n] *?(?!\\n|\n)[\S].+?)(?=\\n|\n)",'COMMENT')
variablepattern = (r'(?:(?:(?:(?:[a-zA-Z_](?:\.\w|\w)*)(?:\[\w*?:?\w*?\])*? *?, *?)*(?:[a-zA-Z_](?:\.\w|\w)*)(?:\[\w*?:?\w*?\])*?)(?= *=))|[a-zA-Z_](?:\.\w|\w)*_+(?:\.\w|\w)*','VARIABLE')
operandpattern = (r'(?<=[+\-*/%=><]) *(?:[\w[({][^+\-*/%=><\n]*)|(?:(?:True|False)(?= *?.*?:))', 'OPERAND')
URLpattern = (r'(?:(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w \.-]*)*\/?)','URL')
operatorpattern = (r"""(?:[+\-*/%:=><^!|~&]{1,3})|\b(?:and|if|else|elif|for|while|try|except|finally|with|as|class|not|is|in|or|xor|def)(?= *.*?:)|(?:\\n|\n)\s*(?:break|continue)\s*(?:\\n|\n)|(?:(?<=\n)|(?<=\\n))\s*return(?= .+?\n|\\n)""", 'OPERATOR')

POS_patterns = [methodpattern,stringpattern,commentpattern,variablepattern,operandpattern,URLpattern,operatorpattern]

pattern = r'(?:' + POS_patterns[0][0] + r'|' + POS_patterns[1][0] + r'|' + POS_patterns[2][0] + r'|' + POS_patterns[3][0] + r'|' + POS_patterns[4][0] + r'|' + POS_patterns[5][0] + r'|' + POS_patterns[6][0]+ r')'
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
operands = []
URLs = []
i = 0

print('time taken to prepare dataset: %f' %(time.time()-start))

########################################################################

def sentencetokenize(data, pattern):

    patt = r'(?: *)(?:' + pattern + r')'
    sentences = []
    for i in range(len(data)):
        p=0
        j=0
        while j < len(data[i]['question']):
            if data[i]['question'][j] == '\n':
                if j == 0:
                    data[i]['question'] = data[i]['question'][1:]
                    continue
                elif j < len(data[i]['question']) - 1 and data[i]['question'][j+1] == '\n':
                    data[i]['question'] = data[i]['question'][:j]+''+data[i]['question'][j+1:]
                    p=j
                    continue
                else:
                    data[i]['question'] = data[i]['question'][:j]+'NEWlineHERE. NEWlineHERE'+data[i]['question'][j+1:]
                    j+=23
                p = j
            j+=1

        for k in range(len(data[i]['answers'])):
            p=0
            j=0
            while j < len(data[i]['answers'][k]):
                if data[i]['answers'][k][j] == '\n':
                    if j == 0:
                        data[i]['answers'][k] = data[i]['answers'][k][1:]
                        continue
                    elif j < len(data[i]['answers'][k]) - 1 and data[i]['answers'][k][j+1] == '\n':
                        data[i]['answers'][k] = data[i]['answers'][k][:j]+''+data[i]['answers'][k][j+1:]
                        p=j
                        continue
                    else:
                        data[i]['answers'][k] = data[i]['answers'][k][:j]+'NEWlineHERE. NEWlineHERE'+data[i]['answers'][k][j+1:]
                        j+=23
                    p = j
                j+=1

        for sent in sent_tokenize(data[i]['question']):
            if len(sent)>2:
                sent = re.sub(r'NEWlineHERE\.$','',sent)
                sent = re.sub(r'^NEWlineHERE','',sent)
                sentences.append(sent.lower())
        for texts in data[i]['answers']:
            for sent in sent_tokenize(texts):
                if len(sent)>2:
                    sent = re.sub(r'NEWlineHERE\.$','',sent)
                    sent = re.sub(r'^NEWlineHERE','',sent)
                    sentences.append(sent.lower())
    return sentences

##############       tokenize dataset                  ##############

## remove tokenized data from the dataset so that word_tokenize() will not duplicate existing tokens 2 seconds
start = time.time()
for i in range(len(dataset)):

    #questions
    tokens = regexp_tokenize(dataset[i]['question'], methodpattern[0])
    for l in range(len(tokens)):
        methods.append(tokens[l].lower())
        newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')
    tokens = regexp_tokenize(dataset[i]['question'], stringpattern[0])
    for l in range(len(tokens)):
        strings.append(tokens[l].lower())
        newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')
    tokens = regexp_tokenize(dataset[i]['question'], commentpattern[0])
    for l in range(len(tokens)):
        comments.append(re.sub('\s+?$', '', tokens[l].lower()))
        newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')
    tokens = regexp_tokenize(dataset[i]['question'], variablepattern[0])
    for l in range(len(tokens)):
        variables.append(tokens[l].lower())
##          newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')
    tokens = regexp_tokenize(dataset[i]['question'], URLpattern[0])
    for l in range(len(tokens)):
        URLs.append(tokens[l].lower())
        newdataset[i]['question'] = newdataset[i]['question'].replace(tokens[l],'')

    #answers
    for j in range(len(dataset[i]['answers'])):
        tokens = regexp_tokenize(dataset[i]['answers'][j], methodpattern[0])
        for l in range(len(tokens)):
            methods.append(tokens[l].lower())
            newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')
        tokens = regexp_tokenize(dataset[i]['answers'][j], stringpattern[0])
        for l in range(len(tokens)):
            strings.append(tokens[l].lower())
            newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')
        tokens = regexp_tokenize(dataset[i]['answers'][j], commentpattern[0])
        for l in range(len(tokens)):
            comments.append(re.sub('\s+?$', '', tokens[l].lower()))
            newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')
        tokens = regexp_tokenize(dataset[i]['answers'][j], variablepattern[0])
        for l in range(len(tokens)):
            variables.append(tokens[l].lower())
##          newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')
        tokens = regexp_tokenize(dataset[i]['answers'][j], URLpattern[0])
        for l in range(len(tokens)):
            URLs.append(tokens[l].lower())
            newdataset[i]['answers'][j] = newdataset[i]['answers'][j].replace(tokens[l],'')


print('time taken to tokenize: %f' %(time.time()-start))

##          using word_tokenize() on english words 337 seconds

start = time.time()

sentences = sentencetokenize(newdataset, pattern)

for sent in sentences:
    for token in word_tokenize(sent):
        if len(token) > 1 and token not in stop_words and token not in contractions and not re.search("^[\W\d]+$", token) and token not in set(variables):
            mywords.append(token)

########################################################################



textDist = FreqDist(methods+strings+comments+URLs+variables+mywords)
print('time taken to word_tokenize: %f' %(time.time()-start))


#########           checking for irregular words        ####################

irregularWords = []
print('there are ' + str(len(mywords)) + ' english words.')
start = time.time()
for token in mywords:
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
                    f.write("%s\n" % re.sub(r'\.+$','',word))
    f.write('%s\n' %'#######################################')

print('time taken to consolidate irregulars: %f' %(time.time()-start))

############################################################################################


###############             tokenize dataset into sentences               ####################

start = time.time()

sentences = sentencetokenize(dataset_IR, pattern)


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
        if i % 10000000 == 0:
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
        irregularSentence = irregularWordSentence[int(r)][1][:]
        tokens = list(set(regexp_tokenize(irregularSentence, pattern)))
        for l in range(len(tokens)):
            if len(tokens[l])>3:
                irregularSentence = re.sub(re.escape(tokens[l]),'',irregularSentence, count = 1)
                irregularSentence = re.sub(re.escape('\n'),' ', irregularSentence)
        for token in word_tokenize(irregularWordSentence[int(r)][1]):
            if token not in tokens:
                tokens.append(token)
        for w in pythontagger.tag(tokens):
            f.write("%s\n" % str(w))
    f.write('%s\n' %'#######################################')

########################################################################
