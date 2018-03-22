from __future__ import print_function

import numpy as np
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
#from lxml import etree
import jieba

#def parse_description(desc):
			
def main():
	global featureWordList

	tree = ElementTree.parse('img80.xml')
	root = tree.getroot()
	
	#channel = root.find('channel')
	#issue = channel.find('item')
	desc = root.find('description')
	
	
	
	text = '<rss>'+desc.text.replace("<br/>", "")+'</rss>'
	#print(text)
	text = text.encode('utf-8')
	desc_root = ElementTree.fromstring(text)
	print(''.join(desc_root.itertext()))
	#for element in desc_root.iter():
		#print(element, ', ', element.text)
		#print(p.text)
		#print(element.text)
		#if element.text != None:
		#	print('token = {}'.format(element.text.encode('utf-8')))

main()
