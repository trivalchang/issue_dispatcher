from __future__ import print_function

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree

class mantis_xml_reader:
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
			
	def getIssueInfo(self):
		for issue in self.root.findall('issue'):
			id = issue.find('id').text
			desc = issue.find('description').text
			print('issue ID is {}'.format(issue.find('id').text))
			yield(id, desc)
			
def main():
	issue_parser = mantis_xml_reader('exported_issues.xml')
	#issue_parser = mantis_xml_reader('img80.xml')
	issue_parser.basicInfo()
	#issue_parser.getIssueInfo()
	for (id, desc) in issue_parser.getIssueInfo():
		print('==== ID {}'.format(id))
		print(desc)
main()
