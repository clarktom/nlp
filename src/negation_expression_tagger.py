from nltk import *
import json
from bs4 import BeautifulSoup
import re
import random
import string
import time
import pprint

methodpattern = (r"(?:\b)(?:[a-zA-Z_])(?:\.\w|\w)*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\)[^\(\)]*)*\)[^\(\)]*)*\))",'METHOD')
stringpattern = (r"(?:(?<!\w)|r)(?:(?:\"{3}.+?\"{3})|(?:'{3}.+?'{3})|(?:\"(?:(?!\\n)[^\"])+?\")|(?:'(?:(?!\\n)[^'])+?'))(?!\w)",'STRING')
commentpattern = (r"(?:#[^#\n] *?(?!\\n|\n)[\S].+?)(?=\\n|\n)",'COMMENT')
variablepattern = (r'(?:(?:(?:(?:[a-zA-Z_](?:\.\w|\w)*)(?:\[\w*?:?\w*?\])*? *?, *?)*(?:[a-zA-Z_](?:\.\w|\w)*)(?:\[\w*?:?\w*?\])*?)(?= *=))|[a-zA-Z_](?:\.\w|\w)*_+(?:\.\w|\w)*','VARIABLE')
operandpattern = (r'(?<=[+\-*/%=><]) *(?:[\w[({][^+\-*/%=><\n]*)|(?:(?:True|False)(?= *?.*?:))', 'OPERAND')
URLpattern = (r'(?:(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w \.-]*)*\/?)','URL')
operatorpattern = (r"""(?:[+\-*%=><^!|~&]{1,3})|\b(?:and|if|else|elif|for|while|try|except|finally|with|as|class|not|is|in|or|xor|def)(?= *.*?:)|(?:\\n|\n)\s*(?:break|continue)\s*(?:\\n|\n)|(?:(?<=\n)|(?<=\\n))\s*return(?= .+?\n|\\n)""", 'OPERATOR')

POS_patterns = [methodpattern,stringpattern,commentpattern,variablepattern,operandpattern,URLpattern,operatorpattern]

pattern = r'(?:' + POS_patterns[0][0] + r'|' + POS_patterns[1][0] + r'|' + POS_patterns[2][0] + r'|' + POS_patterns[3][0] + r'|' + POS_patterns[4][0] + r'|' + POS_patterns[5][0] + r'|' + POS_patterns[6][0]+ r')'

# negationExpressionPattern = [(r"(?:[^.?!:\r\n]*(?:No|Not|Neither|Never|No one|Nobody|None|Nor|Nothing|Nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:no|not|neither|never|no one|nobody|none|nor|nothing|nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*(?:n(?:'|’)t|less)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:few|hardly|little|rarely|scarcely|seldom)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:de|dis|un)[^.?!:]*(?:\.|\?|!|:))",'NEGATION')]
# negationExpressionPattern = [(r"(?:[^.?!:\r\n]*(?:No|Not|Neither|Never|No one|Nobody|None|Nor|Nothing|Nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:no|not|neither|never|no one|nobody|none|nor|nothing|nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*(?:n(?:'|’)t|less)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:few|hardly|little|rarely|scarcely|seldom)\b[^.?!:]*(?:\.|\?|!|:))",'NEGATION')]
negationExpressionPattern = (r"(?:[^.?!:\r\n]*(?:No|Not|Neither|Never|No one|Nobody|None|Nor|Nothing|Nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:no|not|neither|never|no one|nobody|none|nor|nothing|nowhere)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*(?:n(?:'|’)t)\b[^.?!:]*(?:\.|\?|!|:))|(?:[^.?!:\r\n]*\b(?:few|hardly|little|rarely|scarcely|seldom)\b[^.?!:]*(?:\.|\?|!|:))",'NEGATION')

with open('dirty_result.json', encoding = 'utf-8', mode='r') as f:
    try:
        dataset = json.load(f)
        for i in range(len(dataset)):
            dataset[i]['question'] = BeautifulSoup(dataset[i]['question'], 'html.parser').get_text()
            for j in range(len(dataset[i]['answers'])):
                dataset[i]['answers'][j] = BeautifulSoup(dataset[i]['answers'][j], 'html.parser').get_text()

    except Exception as e:
        print(e)

negations = []
contractions = set(["n't", "'s", "s'", "'d", "'ll" , "'ve", "'re", "'m"] + [x for x in string.punctuation] + [ x for x in '0123456789'])



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
                    sent = re.sub(r'^\s+','',sent)
                    sent = re.sub(r'\s+$','',sent)
                    sentences.append(sent.lower())
    return sentences

sentences = sentencetokenize(dataset, pattern)

for i in range(len(sentences)):
    tokens = regexp_tokenize(sentences[i], negationExpressionPattern[0])
    for l in range(len(tokens)):
        negations.append(tokens[l].lower())
negations = list(set(negations))
with open('negations_found.txt', encoding="utf-8",mode='w') as f:
    f.write("\n#######################################################\n")
    for i in range(len(negations)):
        f.write(negations[i])
        f.write("\n#######################################################\n")
