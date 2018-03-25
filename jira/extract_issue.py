from __future__ import print_function

import os
import sys
import io

import numpy as np
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from collections import OrderedDict

#from lxml import etree
import jieba
from hanziconv import HanziConv

sys.path.append('/Users/developer/guru/utility')
from fileOp.h5_dataset import h5_dump_dataset, h5_load_dataset

from tf_idf import form_codebook, print_codebook, comput_tf_idf

ENG_NUM = 0
CH = 1

codebook = None
issueWordList = dict()
issueFeatureList = dict()
issueLabelList = dict()
myDict = []

class jira_xml_reader:
	root = None
	def __init__(self, fname):
		tree = ElementTree.parse(fname)
		self.root = tree.getroot()
		print('self.root = {}'.format(self.root))
		
	def basicInfo(self):
		try:
			if (self.root != None):
				print('xml open OK')
		except:
			print('xml open error!')

	def parseDesc(self, desc):
		lines = ''
		if desc.text == None:
			return lines
		text = '<rss>'+desc.text.replace("<br/>", "").replace('&nbsp;', '')+'</rss>'
		text = text.encode('utf-8')
		try:
			desc_root = ElementTree.fromstring(text)
		except:
			print('=========error========')
			print(text)
		if desc_root == None:
			print('can not decode description')
			return lines
		lines = lines.join(desc_root.itertext())
		#for element in desc_root.iter():
			#if element.text != None:
				#lines.append(element.text)			
		
		return lines
		
	def getIssueInfo(self):
		channel = self.root.find('channel')
		for issue in channel.findall('item'):
			title = issue.find('title').text
			summary = issue.find('summary').text
			key = issue.find('key').text
			desc = self.parseDesc(issue.find('description'))
			#desc = issue.find('description').text

			
			yield(title, summary, key, desc)
			

def prune_text(str):
	str = str.replace("<p>", "")
	str = str.replace("</p>", "")
	str = str.replace("<br/>", "")
	str = str.replace("[", " ")
	str = str.replace("]", " ")
	str = str.replace(",", " ")
	str = str.replace(":", " ")
	str = str.replace("\\", " ")
	str = str.replace("/", " ")
	str = str.replace("\n", " ")
	str = str.replace("\r", " ")
	return str

def is_eng_num(ch):
	if ( ch >= u'\u0041' and ch <= u'\u005A' ) or ( ch >= u'\u0061' and ch <= u'\u007A'):
		return True
	if (ch >= u'\u0030' and ch <= u'\u0039'):
		return True
	return False
	
def is_chinese(ch):
	if ch >= u'\u4E00' and ch <= u'\u9FA5':
		return True
	return False	
	
def is_space(ch):
	if ch == u'\u0020':
		return True
	return False	
	
def is_valid(ch):
	validchar = u' ._'
	return ch in validchar
	

def discard_word(coding, word):
	if coding == ENG_NUM and len(word) < 2:
		return True
	return False

def readDict(fname):
	f = io.open(fname, mode='r', encoding="utf-8")
	for line in f:
		myDict.append(line.replace('\n', ''))
	f.close()

def extract_MyDict(sentence):
	words = []
	for w in myDict:
		if w in sentence:
			words.append(w)
			sentence = sentence.replace(w, '')
	return (words, sentence)

def extract_words(str):
	wordList = []
	sentence = ''
	currentEncoding = -1
	encoding = -1
	#str = HanziConv.toTraditional(str)
	for ch in str:
		#print(ch)
		valid = False
		if is_eng_num(ch):
			encoding = ENG_NUM
			valid = True
		if is_chinese(ch):
			encoding = CH
			valid = True
		if is_valid(ch):
			valid = True
		
		if valid == False:
			ch = u' '

		#if valid == True:
			#sentence = sentence + ch

		if encoding != currentEncoding or is_space(ch):
			sentence = sentence.replace(u" ", "")

			if currentEncoding != -1 and len(sentence) != 0:
				sentence = sentence.replace(u" ", "")

			#print('sentence = ', sentence)
			words, sentence = extract_MyDict(sentence)
			if encoding == ENG_NUM:
				if sentence != '':
					words.append(sentence)
			if encoding == CH:
				for w in jieba.cut(sentence, cut_all=False):
					words.append(w)

			for word in words:
				if word == '':
					continue
				if discard_word(currentEncoding, word) == False:
					wordList.append((currentEncoding, word))
			sentence = ''	
		sentence = sentence + ch
		currentEncoding = encoding
		#sentence = sentence + ch
		
	return wordList

#fileList = ['jira_all_1.xml', 'jira_all.xml', 'FREEWVIEW.xml']
fileList = ['AND_CLOSED.xml']
#fileList = ['ML3RTANOM-461.xml']
#fileList = ['img80.xml']			
def main():
	global featureWordList

	readDict("mydict.txt")
	issue_cnt = 0
	for f in fileList:
		issue_parser = jira_xml_reader(f)
		issue_parser.basicInfo()

		for (title, summary, key, desc) in issue_parser.getIssueInfo():
			words = []
			issue_cnt = issue_cnt + 1

			title = prune_text(title)
			words += extract_words(title)		

			summary = prune_text(summary)
			words += extract_words(summary)
			
			key = prune_text(key)
			issueWordList[key] = []
			issueFeatureList[key] = []

			desc = prune_text(desc)
			words += extract_words(desc)

			for w in words:
				if w[1] not in key and w[1].isdigit() == False:
					issueWordList[key].append(w[1])

	print('\n\nTotal Issue         {}'.format(issue_cnt))
	codebook = form_codebook(issueWordList)
	print_codebook(codebook)
	for (key, words) in issueWordList.items():
		issueFeatureList[key] = comput_tf_idf(words, codebook, len(codebook))
		issueLabelList[key] = 100

		#print('[{}] = {}'.format(key, issueFeatureList[key]))

	h5_dump_dataset([f for (k, f) in issueFeatureList.items()], 
					[l for (k, l) in issueLabelList.items()], 
					'issueFeature.hdf5', 
					'issue',
					'w')
		
main()
