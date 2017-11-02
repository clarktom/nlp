import sys, os
sys.path.append("C:/Users/tompu/dev/nlp/src/bratreader")
from bratreader.repomodel import RepoModel
import pprint

r = RepoModel("../annotations") # load repomodel
r.documents            			    # all documents in your brat corpus

doc = r.documents["2"] 			# get document with key 001
# print(doc.sentences)    			# a list of sentences in document
# print(doc.annotations)  			# the annotation objects in a document

for word in doc.annotations:
    print(word.repr, word.labels)

# # Save to XML
# r.save_xml("my_folder")
# # This creates one XML document per original document
# # in the specified folder.