from __future__ import print_function

import numpy as np
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
#from lxml import etree
import jieba

ENG_NUM = 0
CH = 1

featureWordList = []

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
		lines = []
		text = '<rss>'+desc.text.replace("<br/>", "")+'</rss>'
		text = text.encode('utf-8')
		desc_root = ElementTree.fromstring(text)
		if desc_root == None:
			print('can not decode description')
			return lines
		for p in desc_root.findall('p'):
			lines.append(p.text)
		return lines
		
	def getIssueInfo(self):
		channel = self.root.find('channel')
		for issue in channel.findall('item'):
			summary = issue.find('summary').text
			desc = self.parseDesc(issue.find('description'))
			#desc = issue.find('description').text

			key = issue.find('key').text
			yield(summary, key, desc)
			

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
	
def extract_words(str):
	wordList = []
	sentence = ''
	currentEncoding = -1
	encoding = -1
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
		if encoding != currentEncoding or is_space(ch):
			sentence = sentence.replace(u" ", "")
			if currentEncoding != -1 and len(sentence) != 0:
				sentence = sentence.replace(u" ", "")
				if encoding == ENG_NUM:
					wordList.append((currentEncoding, sentence))
					#print('token  ', currentEncoding, sentence)
				elif encoding == CH:
					words = jieba.cut(sentence, cut_all=False)
					for word in words:
						wordList.append((currentEncoding, word))
						#print('token  ', currentEncoding, word)
				sentence = ''	
		currentEncoding = encoding
		sentence = sentence + ch
		
	return wordList

def addFeature(words):
	global featureWordList
	
	npWords = np.array(words)
	for w in np.unique(words):
		if w not in featureWordList:
			featureWordList.append(w)
		
			
def main():
	global featureWordList

	issue_parser = jira_xml_reader('ML3RTANOM-375.xml')
	#issue_parser = jira_xml_reader('jira_all_1.xml')
	#issue_parser = jira_xml_reader('img80.xml')
	issue_parser.basicInfo()
	keywordList = []
	#issue_parser.getIssueInfo()
	issue_cnt = 0
	for (summary, key, desc) in issue_parser.getIssueInfo():
		words = []
		issue_cnt = issue_cnt + 1
		#print('========== summary ============ ')
		summary = prune_text(summary)
		#print(summary)
		words += extract_words(summary)
		#print('========== key ============ ')
		key = prune_text(key)
		words += extract_words(key)
		#print(key)
		print('========== description ============ ')
		#print(desc)
		for line in desc:
			#print(line)
			line = prune_text(line)
			words += extract_words(line)
		addFeature(words)

	print('\n\nTotal Issue         {}'.format(issue_cnt))
	print('feature space      {}'.format(len(featureWordList)))
	for f in featureWordList:
		print('token = {}'.format(f.encode('utf-8')))

main()
