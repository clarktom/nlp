import sys, os
sys.path.append("./bratreader")
from bratreader.repomodel import RepoModel
import pprint
from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string
import time
import copy
import glob
import numpy as np
files = glob.glob("../annotations/*.txt")

def sentencetokenize(text, pattern):
    patt = r'(?: *)(?:' + pattern + r')'
    sentences = []
    p=0
    j=0
    while j < len(text):
        if text[j] == '\n':
            if j == 0:
                text = text[1:]
                continue
            elif j < len(text) - 1 and text[j+1] == '\n':
                text = text[:j]+''+text[j+1:]
                p=j
                continue
            else:
                text = text[:j]+'NEWlineHERE. NEWlineHERE'+text[j+1:]
                j+=23
            p = j
        j+=1
    for sent in sent_tokenize(text):
        if len(sent)>2:
            sent = re.sub(r'NEWlineHERE\.$','',sent)
            sent = re.sub(r'^NEWlineHERE','',sent)
            sent = re.sub(r'^\s+','',sent)
            sent = re.sub(r'\s+$','',sent)
            sentences.append(sent.lower())
    return sentences

methodpattern = (r"(?:\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))",'METHOD')
stringpattern = (r"(?:(?<!\w)|r)(?:(?:\"{3}.+?\"{3})|(?:'{3}.+?'{3})|(?:\"(?:(?!\\n)[^\"])+?\")|(?:'(?:(?!\\n)[^'])+?'))(?!\w)",'STRING')
commentpattern = (r"(?:#[^#\n] *?(?!\\n|\n)[\S].+?)(?=\\n|\n)",'COMMENT')
variablepattern = (r'(?:(?:(?:(?:[a-zA-Z_](?:\.\w|\w)*)(?:\[\w*?:?\w*?\])*? *?, *?)*(?:[a-zA-Z_](?:\.\w|\w)*)(?:\[\w*?:?\w*?\])*?)(?= *=))|[a-zA-Z_](?:\.\w|\w)*_+(?:\.\w|\w)*','VARIABLE')
operandpattern = (r'(?<=[+\-*/%=><]) *(?:[\w[({][^+\-*/%=><\n]*)|(?:(?:True|False)(?= *?.*?:))', 'OPERAND')
URLpattern = (r'(?:(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w \.-]*)*\/?)','URL')
operatorpattern = (r"""(?:[+\-*%=><^!|~&]{1,3})|\b(?:and|if|else|elif|for|while|try|except|finally|with|as|class|not|is|in|or|xor|def)(?= *.*?:)|(?:\\n|\n)\s*(?:break|continue)\s*(?:\\n|\n)|(?:(?<=\n)|(?<=\\n))\s*return(?= .+?\n|\\n)""", 'OPERATOR')

POS_patterns = [methodpattern,stringpattern,commentpattern,variablepattern,operandpattern,URLpattern,operatorpattern]

pattern = r'(?:' + POS_patterns[0][0] + r'|' + POS_patterns[1][0] + r'|' + POS_patterns[2][0] + r'|' + POS_patterns[3][0] + r'|' + POS_patterns[4][0] + r'|' + POS_patterns[5][0] + r'|' + POS_patterns[6][0]+ r')'

stop_words = set(corpus.stopwords.words("english"))
contractions = set(["n't", "'s", "s'", "'d", "'ll" , "'ve", "'re", "'m"] + [x for x in string.punctuation] + [ x for x in '0123456789'])
mydict = set([x.lower() for x in corpus.words.words()])
ps = stem.PorterStemmer()
lmtzr = stem.wordnet.WordNetLemmatizer()
tagger_path = r'english.pickle'
default_tagger = data.load(tagger_path)
pythontagger = RegexpTagger(POS_patterns, backoff = default_tagger)

# Read txt files and save text in dict
posts = dict()
for path in files:
    with open(path, mode='r') as f:
        filename = path.split("\\")[1].split(".")[0]
        posts[filename] = dict()
        posts[filename]["text"] = f.read()
        posts[filename]["newtext"] = copy.deepcopy(posts[filename]["text"])

for filename, post in posts.items():
    print("Analysing post", filename)

    methods = []
    strings = []
    comments = []
    variables = []
    mywords = []
    operands = []
    operators = []
    URLs = []
    alltokens = []

    tokens = regexp_tokenize(post["text"], methodpattern[0])
    for l in range(len(tokens)):
        methods.append(tokens[l].lower())
        post["newtext"] = post["text"].replace(tokens[l],'')
    tokens = regexp_tokenize(post["text"], stringpattern[0])
    for l in range(len(tokens)):
        strings.append(tokens[l].lower())
        post["newtext"] = post["text"].replace(tokens[l],'')
    tokens = regexp_tokenize(post["text"], commentpattern[0])
    for l in range(len(tokens)):
        comments.append(re.sub('\s+?$', '', tokens[l].lower()))
        post["newtext"] = post["text"].replace(tokens[l],'')
    tokens = regexp_tokenize(post["text"], variablepattern[0])
    for l in range(len(tokens)):
        variables.append(re.sub('\s+?$', '', tokens[l].lower()))
        if len(tokens[l])>3:
            post["newtext"] = post["text"].replace(tokens[l],'')
    tokens = regexp_tokenize(post["text"], operandpattern[0])
    for l in range(len(tokens)):
        operands.append(re.sub('\s+?$', '', tokens[l].lower()))
        if len(tokens[l])>3:
            post["newtext"] = post["text"].replace(tokens[l],'')
    tokens = regexp_tokenize(post["text"], URLpattern[0])
    for l in range(len(tokens)):
        URLs.append(tokens[l].lower())
        post["newtext"] = post["text"].replace(tokens[l],'')
    tokens = regexp_tokenize(post["text"], operatorpattern[0])
    for l in range(len(tokens)):
        operators.append(tokens[l].lower())
        post["newtext"] = post["text"].replace(tokens[l],'')
            
    sentences = sentencetokenize(post["newtext"], pattern)
    for sent in sentences:
        # print("sent:", sent)
        for token in word_tokenize(sent):
            # print("token:", token)
            if len(token) > 1 and token not in stop_words and token not in contractions and not re.search("^[\W\d]+$", token) and token not in set(methods+strings+comments+operands+operators+variables+URLs):
                mywords.append(token)

    alltokens = set(methods+strings+comments+operands+operators+mywords+variables+URLs)
    post["words"] = pythontagger.tag(list(alltokens))

# -------- 

r = RepoModel("../annotations")     # load repomodel
r.documents            			    # all documents in your brat corpus

filename = "9"
doc = r.documents[filename] 			# get document with key 001
# print(doc.sentences)    			# a list of sentences in document
# print(doc.annotations)  			# the annotation objects in a document

# for word in doc.annotations:
#     print(word.repr, word.labels)

for filename, post in posts.items():
    doc = r.documents[filename]
    words = []
    for word in doc.annotations:
        words.append((word.repr, word.labels))
    # print("")
    # print(words)
    words = list(set(words))
    # print(words)
    doc.annotations = words
    # print(doc.annotations)

# print(posts[filename]["repr"])
results = []
for filename, post in posts.items():
    print("")
    print("Post:", filename)
    ## --------------- Manual against Tokenizer
    doc = r.documents[filename] 
    for word in doc.annotations:
        
        print("     Manual annotation:", word[0], word[1])
        result = 0
        matches = [x for x in posts[filename]["words"] if x[0].lower() == word[0].lower()]
        print("         Tokenizer matches:", matches)
        for match in matches:
            result = 1
            # print(match[1].lower(), word.labels.lower())
            if (match[1].lower()[0] in word[1].lower()) or (word[1].lower() in match[1].lower()[0]):
                result = 2
                print("         POS tag match !")
        results.append(result)


    # # --------------- Tokenizer against Manual
    # for word in posts[filename]["words"]:
    #     print("Tokenizer:", word[0], word[1])
    #     result = 0
    #     doc = r.documents[filename]
    #     ann = []
    #     for w in doc.annotations:
    #         # print(w.repr)
    #         # print(w.labels)
    #         ann.append((w.repr, w.labels))
    #         # print(word.repr, word.labels)
    #     # print(ann)
    #     matches = [x for x in ann if x[0].lower() == word[0].lower()]
    #     print("     ", matches)
    #     for match in matches:
    #         result = 1
    #         print("Token matches:", match)
    #         # print(match[1].lower(), word.labels.lower())
    #         if (match[1].lower()[0] in word[1].lower()) or (word[1].lower() in match[1].lower()[0]):
    #             result = 2
    #             print("POS tag match !")
    #     results.append(result)



unique, counts = np.unique(results, return_counts=True)
print(np.asarray((unique, counts)).T)
print(len(results))


        # for word in posts[filename]["words"]:
        #     print("Tokenizer:", word[0], word[1])
    
