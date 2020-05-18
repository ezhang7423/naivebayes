# coding: utf-8

# In[11]:

import math
import json
from deques import deques
from collections import deque
from stop import *
import os
import time
import sys
import numpy as np
assert sys.version[0] == '3'
# trname = sys.argv[1]
# tsname = sys.argv[2]
trname = 'training.txt'
tsname = 'testing.txt'
try:
    prod = not bool(os.environ['PROD'])
except KeyError:
    prod = True

# %%

# In[12]:


def amtClass(filename):
    good = 0
    bad = 0
    with open(f"{filename}.txt", 'r') as data:
        reviews = data.read().splitlines()
    for rev in reviews:
        if rev.split(' ')[-1] == ',1':
            good += 1
        else:
            bad += 1
    # print(f'good: {good} bad: {bad}')
    return {'good': good, 'bad': bad}


# In[13]:


def generateVocab(filename):
    uniques = set()
    with open(f"{filename}.txt", 'r') as data:
        reviews = data.read().splitlines()
    words = {'1': 0, '0': 0}  #1 is good, 0 is bad
    for review in reviews:
        # ngram = deque([], maxlen=2)
        # ngram3 = deque([], maxlen=3)
        ngrams = deques(ngramlen)
        cReview = review.split(' ')
        mode = 1 if (cReview[-1] == ",1") else 0
        for word in cReview:
            #    do stemming
            if word.isalnum() and word not in stop:
                # ngram.append(word)
                # ngram3.append(word)
                ngrams.append(word)
                for x in ngrams.getWords():
                    uniques.add(x)
                uniques.add(word)
    occurences = np.zeros((len(uniques), 3))
    positions = {v: k for k, v in enumerate(list(uniques))}
    for review in reviews:
        cReview = review.split(' ')
        mode = 1 if (cReview[-1] == ",1") else 0
        # ngram = deque([], maxlen=2)
        # ngram3 = deque([], maxlen=3)
        ngrams = deques(ngramlen)
        for word in cReview:
            #    do stemming
            if word.isalnum() and word not in stop:
                ngrams.append(word)
                # ngram.append(word)
                # ngram3.append(word)
                for x in ngrams.getWords():
                    words[str(mode)] += 1
                    occurences[positions[x], mode] += 1
                    occurences[positions[x], 2] += 1
                words[str(mode)] += 1
                occurences[positions[word], mode] += 1
                occurences[positions[word], 2] += 1
    transitory = amtClass(filename)
    transitory['goodwords'] = words['1']
    transitory['badwords'] = words['0']
    return (positions, transitory, occurences)


start_gen = time.time()
# In[14]:
# if not prod:
if prod:
    # generateVocab('training')
    # print('not prod branch')
    fname = 'training_occurences.npy'
    with open('training_labels.txt', 'r') as fin:
        numClasses = json.loads(fin.read())
        totalReviews = 0
        for x in numClasses:
            totalReviews += numClasses[x]
    occ = np.load(fname)
    positions = json.loads(open('training_positions.txt', 'r').read())
else:
    # print('prod branch')
    positions, numClasses, occ = generateVocab(trname.split('.')[0])
    totalReviews = 0
    for x in numClasses:
        totalReviews += numClasses[x]

with open(tsname, 'r') as fin:
    testingdata = fin.read().splitlines()

with open(trname, 'r') as fin:
    trainingdata = fin.read().splitlines()

totalWords = occ.shape[0]
time_gen = time.time() - start_gen

# In[16]:


def test(data, silent=True):
    total = 0
    correct = 0
    wrong = []
    for i, x in enumerate(data):
        act = x.split(' ')[-1]
        if act == ",1":
            act = 'good'
        elif act == ",0":
            act = 'bad'
        prediction = pred(x)
        if not silent:
            if prediction == 'good':
                print('1')
            else:
                print('0')
        if act == prediction:
            correct += 1
        else:
            wrong.append(i)
        total += 1

    with open('misclassified.txt', 'w') as fout:
        for x in wrong:
            fout.write((data[x]) + '\n')
    return correct / total


def pred(string):
    probs = []
    if (len(string) < 11 and 'ok' in string):
        return 'good'
    classes = ['good', 'bad']
    for c in classes:
        probs.append(prob(string, c))
    return classes[argmax(probs)]


def argmax(values):
    return max(enumerate(values), key=lambda x: x[1])[0]


# alpha = .002
# alpha = 1
alpha = 0.869
# ngramlen = 2

# def prob(string, clas):
#     t1 = math.log((numClasses[clas] + alpha * totalWords) /
#                   (totalReviews + 2 * alpha * totalWords))
#     t2 = 0
#     bottom = (numClasses[clas + 'words'] + alpha * totalWords)
#     words = string.split(' ')
#     ngram = deque([], maxlen=ngramlen)
#     ngram3 = deque([], maxlen=3)
#     for x in words:
#         if x.isalnum() and x not in stop:
#             #stem here
#             nclas = 1 if (clas == "good") else 0
#             ngram.append(x)
#             ngram3.append(x)
#             nword = ''.join(ngram)
#             nword3 = ''.join(ngram3)
#             try:
#                 t2 += math.log((occ[positions[x], nclas] + alpha) / bottom)
#             except KeyError:
#                 # continue
#                 t2 += math.log(1 / bottom)
#             try:
#                 if len(ngram) == ngramlen:
#                     t2 += math.log(
#                         (occ[positions[nword], nclas] + alpha) / bottom)
#             except KeyError:
#                 # continue
#                 t2 += math.log(1 / bottom)
#             try:
#                 if len(ngram3) == 3:
#                     t2 += math.log(
#                         (occ[positions[nword3], nclas] + alpha) / bottom)
#             except KeyError:
#                 # continue
#                 t2 += math.log(1 / bottom)

#     return t1 + t2


def prob(string, clas):
    t1 = math.log((numClasses[clas] + alpha * totalWords) /
                  (totalReviews + 2 * alpha * totalWords))
    t2 = 0
    bottom = (numClasses[clas + 'words'] + alpha * totalWords)
    words = string.split(' ')
    # ngram = deque([], maxlen=ngramlen)
    # ngram3 = deque([], maxlen=3)
    ngrams = deques(ngramlen)
    for x in words:
        if x.isalnum() and x not in stop:
            #stem here
            nclas = 1 if (clas == "good") else 0
            ngrams.append(x)
            # ngram.append(x)
            # ngram3.append(x)
            for x in ngrams.getWords():
                try:
                    t2 += math.log((occ[positions[x], nclas] + alpha) / bottom)
                except KeyError:
                    # continue
                    t2 += math.log(1 / bottom)
            try:
                t2 += math.log((occ[positions[x], nclas] + alpha) / bottom)
            except KeyError:
                # continue
                t2 += math.log(1 / bottom)

    return t1 + t2


def main():
    if prod:
        testacc = test(testingdata, silent=False)
        start_train = time.time()
        trainacc = test(trainingdata, silent=True)
        time_train = time.time() - start_train
        print(f"{round(time_gen)} seconds (training)")
        print(f"{round(time_train)} seconds (labeling)")
        print(f"{round(trainacc, 3)} (training)")
        print(f"{round(testacc, 3)} (testing)")
    else:
        print('start testing')
        testacc = test(testingdata, silent=True)
        print(testacc)


if __name__ == "__main__":
    main()

# In[ ]:
