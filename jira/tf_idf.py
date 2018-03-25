
from __future__ import print_function

import numpy as np
from collections import OrderedDict

featureList = [
	['test', 'computer', 'test', 'monitor', 'my', 'vision'],
	['computer', 'bus', 'car', 'bicycle', 'mac'],
	['shoe', 'flower', 'tree', 'grass'],
	['department', 'branch', 'tree', 'bed', 'window', 'door'],
	['mud', 'car'],
]

def compute_idf(cb, fl):
	n = float(len(fl))

	for (key, value) in cb.items():
		td = 0
		for f in fl:
			if key in f:
				td += 1
		cb[key] = np.log10(n/(1+td))

def form_codebook(samples):
	cb = dict()
	for (key, f) in samples.items():
	#for f in samples:
		#print(key, ' === ', f)
		for w in np.unique(f):
			if (w, 0) not in cb:
				cb[w] = 0
	compute_idf(cb, samples)
	return OrderedDict(sorted(cb.items(), key=lambda x: x[1], reverse=True))

def comput_tf_idf(words, cb, vectorSize):
	feature = []
	for key, idf in cb.items():
		tf = words.count(key)
		tf = np.log10(1+tf)
		feature.append(tf*idf)
		if len(feature) == vectorSize:
			break
	return feature


def print_codebook(cb):	
	for (key, value) in cb.items():
		print(key.encode('utf-8'), '=', value)

def test():
	codebook = form_codebook(featureList)
	print_codebook(codebook)
	for f in featureList:
		fv = comput_tf_idf(f, codebook, len(codebook))
		print(fv)
#test()