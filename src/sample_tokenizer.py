import nltk
import json

with open("../data/dirty_result.json", 'r') as f:
    try:
        dataset = json.load(f)

    except Exception as e:
        print(e)
#########tokenizing###########



stop_words = set(nltk.corpus.stopwords.words("english"))
##words = [[[[token for token in nltk.tokenize.word_tokenize(sent) if '/' not in token and token not in stop_words] for sent in nltk.tokenize.sent_tokenize(texts)] for texts in post['posts']] for post in dataset[:]]
words = []
for post in dataset[:]:
    for texts in post['posts']:
        for sent in nltk.tokenize.sent_tokenize(texts):
            for token in nltk.tokenize.word_tokenize(sent):
                if '/' not in token and token not in stop_words and token not in words :
                    words.append(token)



##########stemming########
ps = nltk.stem.PorterStemmer()

stemmed = []

for w in words:
    stemmed.append(ps.stem(w))

stemmed = set(stemmed)
#######POS tagging##########

postagged = []
for i in nltk.pos_tag(words):
    postagged.append(i)

# Regex list:
#    Variables :   (?:\b)[a-zA-Z]_?\w*(?:\b)
#    Operators :   (?:\b)(\+|-|~|\*|\*\*|/|//|%|<<|>>|&|\||\^|and|or|not|in|not in|is|is not|<|>|!=|<>|==|<=|<>)(?:\b)
#    Delimiters :  (\(|\)|\[|\]|{|}|,|:|\.|`|=|;|\+=|-=|\*=|/=|//=|%=|<=|\|=|\^=|>>=|<<=|\*\*=|'|\"|\\|@)
#    Keywords :    (?:\b)(and|del|global|not|with|as|elif|if|or|yield|assert|else|import|pass|False|break|expect|in|raise|None|class|finally|is|return|True|continue|for|lambda|try|def|from|nonlocal|while)(?:\b)


##train_text = nltk.corpus.state_union.raw("2005-GWBush.txt")
##sample_text = nltk.corpus.state_union.raw("2006-GWBush.txt")
##
##custom_sent_tokenizer = nltk.tokenize.PunktSentenceTokenizer(train_text)
##
##tokenized = custom_sent_tokenizer.tokenize(sample_text)
##
##for i in tokenized:
##    text_words = nltk.word_tokenize(i)
##    tagged = nltk.pos_tag(text_words)
##    print(tagged)

