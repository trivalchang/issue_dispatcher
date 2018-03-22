from __future__ import print_function

import numpy as np
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
#from lxml import etree
import jieba
from hanziconv import HanziConv

ENG_NUM = 0
CH = 1

featureWordList = []
issueWordList = dict()

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
			print('key = ', key)
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

def addFeature(key, words):
	global featureWordList, issueWordList
	
	npWords = np.array(words)
	issueWordList[key] = []

	for w in words:
		issueWordList[key].append(w)
	
	for w in np.unique(words):
		if w not in featureWordList:
			featureWordList.append(w)
			

#fileList = ['jira_all_1.xml', 'jira_all.xml', 'FREEWVIEW.xml']
fileList = ['AND_CLOSED.xml']
#fileList = ['ML3RTANOM-461.xml']
#fileList = ['img80.xml']			
def main():
	global featureWordList
	
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
			
			if key == 'ML3RTANOM-276':
				print('got ', key)
			key = prune_text(key)

			#print(desc)
			#for line in desc:
			#	if key == 'ML3RTANOM-276':
			#		print(line)
			desc = prune_text(desc)
			words += extract_words(desc)
			if key == 'ML3RTANOM-276':
				print('words = ', words)
			addFeature(key, words)

	print('\n\nTotal Issue         {}'.format(issue_cnt))
	print('feature space      {}'.format(len(featureWordList)))
	#for f in featureWordList:
		#print('token = {}'.format(f.encode('utf-8')))
		#print('token = {}'.format(f))

	for key, wl in issueWordList.items():
		if len(wl) < 10:
			print('key = ', key)
			print('		words = ', wl)
		
		
main()
