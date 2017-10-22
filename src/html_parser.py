from bs4 import BeautifulSoup
import json


with open('../data/dirty_result.json', 'r') as f:
    try:
        dataset = json.load(f)

    except Exception as e:
        print(e)


soup = BeautifulSoup((dataset[:1]), 'html.parser')

print(soup.get_text())



##for post in dataset[:1]:
##    for texts in post['posts']:
##            soup = BeautifulSoup(texts, 'html.parser')
##            print(soup.get_text())
