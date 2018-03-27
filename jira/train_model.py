from __future__ import print_function

import os
import sys
import random
from sklearn.svm import SVC
import pickle

import numpy as np
import argparse

sys.path.append('/Users/developer/guru/utility')

from fileOp.h5_dataset import h5_dump_dataset, h5_load_dataset

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-f", "--feature", required=True,  help="feature file")
	args = vars(ap.parse_args())

	(featureList, labels) = h5_load_dataset(args['feature'], 'issue')
	classInfo = np.unique(labels)
	numClass = len(classInfo)
	print('num of class ', numClass)

	model = SVC(kernel="linear", C=0.01, probability=True, random_state=42)
	model.fit(featureList, labels)

	f = open('classifier.cpickle', "wb")
	f.write(pickle.dumps(model))
	f.close()

	#for (label, feature) in zip(labels, featureList):
	#	print('[{}]: len {} {}'.format(int(label), len(feature), np.count_nonzero(feature)))

main()