# coding=utf-8
import numpy as np
import jieba
import io

myDict = []
def extract_MyDict(sentence):
	words = []
	for w in myDict:
		if w in sentence:
			words.append(w)
			sentence = sentence.replace(w, '')
	if sentence != '':
		words.append(sentence)
	return words

def readDict(fname):
	f = io.open(fname, mode='r', encoding="utf-8")
	for line in f:
		myDict.append(line.replace('\n', ''))
	f.close()


readDict("mydict.txt")
test0 = u"進入測項前先將音量調整"
words = extract_MyDict(test0)
for w in words:
	print(w)
