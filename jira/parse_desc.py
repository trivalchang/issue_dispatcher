from __future__ import print_function

import numpy as np
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
#from lxml import etree
import jieba

#def parse_description(desc):
			
def main():
	global featureWordList

	tree = ElementTree.parse('desc.xml')
	root = tree.getroot()

	for p in root.findall('p'):
		print(p.text)

main()
