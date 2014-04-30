#! /usr/bin/python

import sys
from collections import defaultdict
import math

from count_freqs import simple_conll_corpus_iterator as corpus_iter
from count_freqs import Hmm
from hmm import SimpleTagger


"""
Count word frequencies in a data file and rewrite the RARE(freq<5) words to
_RARE_
"""
def gene_word_iterator(input):
    l = input.readline()
    while l:
        word = l.strip()
        if word:
            yield word
        else:
            yield None
        l = input.readline()

def tag(tagger, input, output):
    i = 0
    for word in gene_word_iterator(input):
        if word:
            output.write("%s %s\n" % (word, tagger.y_star(word)[1]))
        else:
            output.write("\n")
        i = i + 1
        if i % 1000 == 0:
            print i, " lines passed"

def train(tagger, train_filename, rare_filename):
    # 1. read train file, count words
    tagger.count_word(corpus_iter(file(train_filename)))
    # 2. replace rare words
    tagger.replace_rare_tag(corpus_iter(file(train_filename)), 
            file(rare_filename, 'w'))
    # 3. read repalced train file, count ngrams
    tagger.train(file(rare_filename))




def main():
    TRAIN = True
    # 1. training
    train_filename = 'gene.train'
    rare_filename = 'gene.train.rare'

    tagger = SimpleTagger(3)
    train(tagger, train_filename, rare_filename)

    # 2. tagging
    test_filename = 'gene.dev'
    pred_filename = 'gene_dev.p1.out'

    tag(tagger, file(test_filename), file(pred_filename, 'w'))

if __name__ == "__main__":
    main()
