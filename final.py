# coding: utf-8

# In[11]:

import math
import json
from collections import defaultdict
from collections import deque
from stop import *
import os
import time
import sys
import numpy as np
assert sys.version[0] == '3'
trname = sys.argv[1]
tsname = sys.argv[2]
try:
    prod = not bool(os.environ['PROD'])
except KeyError:
    prod = True

# %%

# In[12]:


def amtClass(reviews):
    good = 0
    bad = 0
    for rev in reviews:
        if rev[-1] == '1':
            good += 1
        else:
            bad += 1
    # print(f'good: {good} bad: {bad}')
    return {'good': good, 'bad': bad}


# In[13]:


def generateVocab(reviews):
    uniques = set()
    words = {'1': 0, '0': 0}  #1 is good, 0 is bad
    for review in reviews:
        ngram = deque([], maxlen=2)
        ngram3 = deque([], maxlen=3)
        cReview = review.split(' ')
        mode = 1 if (cReview[-1] == ",1") else 0
        for word in cReview:
            #    do stemming
            if word.isalnum() and word not in stop:
                ngram.append(word)
                ngram3.append(word)
                uniques.add(''.join(ngram))
                uniques.add(''.join(ngram3))
                uniques.add(word)
    occurences = np.zeros((len(uniques), 2))
    positions = {v: k for k, v in enumerate(list(uniques))}
    for review in reviews:
        cReview = review.split(' ')
        mode = 1 if (cReview[-1] == ",1") else 0
        ngram = deque([], maxlen=2)
        ngram3 = deque([], maxlen=3)
        for word in cReview:
            #    do stemming
            if word.isalnum() and word not in stop:
                ngram.append(word)
                ngram3.append(word)
                nword = ''.join(ngram)
                nword3 = ''.join(ngram3)
                if len(ngram) == ngramlen:  # sometimes 2 = one word.
                    words[str(mode)] += 1
                    occurences[positions[nword], mode] += 1
                    # occurences[positions[nword], 2] += 1
                if len(ngram3) == 3:  # sometimes 2 = one word.
                    words[str(mode)] += 1
                    occurences[positions[nword3], mode] += 1
                    # occurences[positions[nword3], 2] += 1
                words[str(mode)] += 1
                occurences[positions[word], mode] += 1
                # occurences[positions[word], 2] += 1
    transitory = amtClass(reviews)
    transitory['goodwords'] = words['1']
    transitory['badwords'] = words['0']
    return (positions, transitory, occurences)


def bine(b, bins):
    bins.append(math.inf)
    i = 0
    binned = []
    temp = []
    for r in b:
        if bins[i] <= len(r) < bins[i + 1]:
            temp.append(r)
        else:
            # print(bins[i])
            binned.append(temp)
            temp = [r]
            i += 1
    binned.append(temp)
    return binned


start_gen = time.time()

with open(trname, 'r') as fin:
    reviews = fin.read().splitlines()

# In[14]:
if not prod:
    store = {}
    # if prod:
    # generateVocab('training')
    # print('not prod branch')
    for b in bins:
        store[b] = {}
        with open(f'data/{b}_labels.txt', 'r') as fin:
            store[b]['numClasses'] = json.loads(fin.read())
            totalReviews = 0
            for x in store[b]['numClasses']:
                totalReviews += store[b]['numClasses'][x]
            store[b]['totalReviews'] = totalReviews
        store[b]['occ'] = np.load(f'data/{b}_occurences.npy')
        store[b]['positions'] = json.loads(
            open(f'data/{b}_positions.txt', 'r').read())
        store[b]['totalWords'] = store[b]['occ'].shape[0]
else:
    reviews.sort(key=len)
    store = {}
    binned = bine(reviews, bins)
    for b, d in zip(bins, binned):
        store[b] = {}
        positions, transitory, occurences = generateVocab(d)
        store[b]['numClasses'] = transitory
        totalReviews = 0
        for x in store[b]['numClasses']:
            totalReviews += store[b]['numClasses'][x]
        store[b]['totalReviews'] = totalReviews
        store[b]['occ'] = occurences
        store[b]['positions'] = positions
        store[b]['totalWords'] = store[b]['occ'].shape[0]

with open(tsname, 'r') as fin:
    testingdata = fin.read().splitlines()
time_gen = time.time() - start_gen
bins.append(math.inf)
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

    if not silent:
        with open('misclassified.txt', 'w') as fout:
            for x in wrong:
                fout.write((data[x]) + '\n')
    return correct / total


def pred(string):
    probs = []
    if (len(string) < 11 and 'ok' in string):
        return 'good'
    if (len(string.split(' ')) == 2):
        if ('a' == string.split(' ')[0] or 'aaa' in string or 'none' in string
                or 'k' == string.split(' ')[0]):
            return 'good'
        elif ('suck' in string or 'bad' in string or 'lame' in string):
            return 'bad'
    classes = ['good', 'bad']
    ls = len(string)
    for i in range(len(bins)):
        if bins[i] <= ls < bins[i + 1]:
            bine = bins[i]
    bine = store[bine]
    for c in classes:
        probs.append(
            prob(string, c, bine['numClasses'], bine['totalWords'],
                 bine['occ'], bine['totalReviews'], bine['positions']))
    return classes[argmax(probs)]


def argmax(values):
    return max(enumerate(values), key=lambda x: x[1])[0]


# alpha = .002
alpha = 1


def prob(string, clas, numClasses, totalWords, occ, totalReviews, positions):
    t1 = math.log((numClasses[clas] + alpha * totalWords) /
                  (totalReviews + 2 * alpha * totalWords))
    t2 = 0
    bottom = (numClasses[clas + 'words'] + alpha * totalWords)
    words = string.split(' ')
    ngram = deque([], maxlen=ngramlen)
    ngram3 = deque([], maxlen=3)
    nclas = 1 if (clas == "good") else 0
    iocc = defaultdict(int)
    for x in words:
        if x.isalnum() and x not in stop:
            ngram.append(x)
            ngram3.append(x)
            nword = ''.join(ngram)
            nword3 = ''.join(ngram3)
            iocc[x] += 1
            if len(ngram) == ngramlen:
                iocc[nword] += 1
            if len(ngram3) == 3:
                iocc[nword3] += 1
    for x in iocc:
        try:
            prob = math.log(iocc[x] + alpha + 1)
            # prob = iocc[x]
            t2 += prob * math.log((occ[positions[x], nclas] + alpha) / bottom)

        except KeyError:
            # continue
            t2 += math.log(1 / bottom)
    return t1 + t2


def main():
    if prod:
        testacc = test(testingdata, silent=False)
        start_train = time.time()
        trainacc = test(reviews, silent=True)
        time_train = time.time() - start_train
        print(f"{round(time_gen)} seconds (training)")
        print(f"{round(time_train)} seconds (labeling)")
        print(f"{round(trainacc, 3)} (training)")
        print(f"{round(testacc, 3)} (testing)")
    else:
        testacc = test(testingdata, silent=True)
        print(testacc)


if __name__ == "__main__":
    main()

# In[ ]:
