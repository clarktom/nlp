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
commentpattern = (r"(?:#[^#\n] *?(?!\n)[\S].+?)(?:\n|$)",'COMMENT')
variablepattern = (r'(?:(?:(?:(?:[a-zA-Z_](?:\.\w|\w)*)(?:\[\w*?:?\w*?\])*? *?, *?)*(?:[a-zA-Z_](?:\.\w|\w)*)(?:\[\w*?:?\w*?\])*?)(?= *=))|[a-zA-Z_](?:\.\w|\w)*_+(?:\.\w|\w)*','VARIABLE')
operandpattern = (r'(?<=[+\-*/%=><]) *(?:[\w[({][^+\-*/%=><\n]*)|(?:(?:True|False)(?= *?.*?:))', 'OPERAND')
URLpattern = (r'(?:(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w \.-]*)*\/?)','URL')
operatorpattern = (r"""(?:[+\-*%=><^!|~&]{1,3})|\b(?:and|if|else|elif|for|while|try|except|finally|with|as|class|not|is|in|or|xor|def)(?= *.*?:)|(?:\n)\s*(?:break|continue)\s*(?:\n)|(?<=\n)\s*return(?= .+?\n)""", 'OPERATOR')

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
##    print("Analysing post", filename)

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
##            if len(token) > 1 and token not in contractions and not re.search("^[\W\d]+$", token) and token not in set(methods+strings+comments+operands+operators+variables+URLs):
            if not re.search("^[\W\d]+$", token) and token not in set(methods+strings+comments+operands+operators+variables+URLs):
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
truePOS = 0
falsePOS = 0
falseNEG = 0
trueNEG = 0
with open('evaluation_data.txt', encoding = 'utf-8', mode = 'w') as f:
    for filename, post in posts.items():
        f.write("\n")
        f.write("Post: ")
        f.write(str(filename))
        ## --------------- Manual against Tokenizer
        doc = r.documents[filename] 
        for word in doc.annotations:
            
            f.write("\n     Manual annotation: ")
            f.write(str(word))
            result = 0
            matches = [x for x in posts[filename]["words"] if x[0].lower() == word[0].lower()]
            f.write("\n         Tokenizer matches: ")
            f.write(str(matches))
            for match in matches:
                result = 1
                # print(match[1].lower(), word.labels.lower())
                if match[1].lower() == 'PRP$'.lower():
                    match = (match[0],'PRP_')
                if (match[1].lower() in word[1].lower()) or (word[1].lower() in match[1].lower()):
                    result = 2
                    f.write("\n             true positive POS tag match: ")
                    f.write(word[1].lower())
                    truePOS += 1
                elif match[1]:
                    falsePOS += 1
                    f.write("\n             false positive POS tag match: ")
                    print("     Manual annotation: ",word)
                    print("         Tokenizer matches: ",matches)
                    print("             false positive POS tag match: ", word[1].lower())
                    f.write(word[1].lower())
                elif pythontagger.tag([match[0]]) == word[1]:
                    falseNEG += 1
                    f.write("\n             false negative POS tag match: ")
                    f.write(word[1].lower())
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


    total = len(results)
    unique, counts = np.unique(results, return_counts=True)
    results = np.asarray((unique, counts)).T
    results[1][1] = results[1][1] + results[2][1]
    f.write('\n')
    f.write(str(results))
    f.write('\n')
    print(results)
    print("\nTotal: ",total)
    f.write(str(total))
    f.write('\nTrue Positives: ')
    print('True Positives: ',truePOS)
    f.write(str(truePOS))
    f.write('\nFalse Positives: ')
    print('False Positives: ',falsePOS)
    f.write(str(falsePOS))
    f.write('\nFalse Negatives: ')
    print('False Negatives: ',falseNEG)
    f.write(str(falseNEG))
    # for word in posts[filename]["words"]:
    #     print("Tokenizer:", word[0], word[1])

    precision = truePOS/(truePOS+falsePOS)
    recall = truePOS/(truePOS+falseNEG)
    f1 = (2*truePOS)/(2*truePOS+falsePOS+falseNEG)
    f.write("\nPrecision: ")
    f.write(str(precision))
    f.write("\nRecall: ")
    f.write(str(recall))
    f.write("\nF1 Score: ")
    f.write(str(f1))
    print('Precision: ',precision)
    print('Recall: ',recall)
    print('F1 Score: ',f1)
    
