# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import math
import json
from collections import defaultdict
from collections import deque
from stop import *
import pprint
import time
import numpy as np
import gc
pp = pprint.PrettyPrinter(indent=4)
# %%


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


# %%


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


def save(filename):
    with open(f"{filename}.txt", 'r') as data:
        reviews = data.read().splitlines()
    reviews.sort(key=len)
    # print(len(reviews[-1]))
    binned = bine(reviews, bins)
    for i, b in enumerate(binned):
        filename = str(bins[i])
        positions, transitory, occurences = generateVocab(b)
        with open('data/' + filename + '_positions.txt', 'w') as fout:
            fout.write(json.dumps(positions))
        np.save('data/' + filename + '_occurences.npy', occurences)
        with open('data/' + filename + '_labels.txt', 'w') as fout:
            fout.write(json.dumps(transitory))


save('training')
