#! /usr/bin/python

import sys
from collections import defaultdict
import math

from count_freqs import simple_conll_corpus_iterator as corpus_iter
from count_freqs import Hmm


"""
Count word frequencies in a data file and replace the RARE(freq<5) words to
RARE_TAG
"""
class SimpleTagger(Hmm):
    """
    Store emissions.
    """
    def __init__(self, n=3):
        super(SimpleTagger, self).__init__(n)

        self.wc = defaultdict(int)
        self.RARE_TAG = '_RARE_'
        self.RARE_THRESHOLD = 5

    def count_word(self, corpus_iterator):
        """
        Count emission probabilities from a corpus file.
        """
        for w in corpus_iterator:
            if w == (None, None):
                continue
            else:
                self.wc[w[0]] += 1

    def replace_rare_tag(self, corpus_iterator, output):
        """
        Replace rare words to _RARE_
        """
        for w in corpus_iterator:
            if w == (None, None):
                output.write("\n")
            else:
                word, ne_tag = w
                if self.wc[word] < self.RARE_THRESHOLD:
                    output.write("%s %s\n" % (self.RARE_TAG, ne_tag))
                else:
                    output.write("%s %s\n" % w)


    def train(self, rare_file):
        super(SimpleTagger, self).train(rare_file)

    def write_count(self, output):
        """
        Writes counts to the output file object.
        """
        for word in self.wc:            
            output.write("%s COUNTS %i\n" % (word, self.wc[word]))

    def argmax_e(self, word):
        def emission_iter(word):
            for e in self.emission_counts.keys():
                if isinstance(e, tuple) and e[0] == word:
                    yield e

        if word not in self.wc or self.wc[word] < self.RARE_THRESHOLD:
            word = self.RARE_TAG
        return max(emission_iter(word), key=
                (lambda key: self.emission_param(key)))

    def y_star(self, word):
        return self.argmax_e(word)

    def emission_param(self, key):
        return float(self.emission_counts[key])\
                / float(self.ngram_counts[0][key[-1:]])


class ViterbiTagger(SimpleTagger):
    def __init__(self, n=3):
        super(ViterbiTagger, self).__init__(n)

    def q_trigram(self, yi, yi_2, yi_1):
        return float(self.ngram_counts[2][(yi_2, yi_1, yi)])\
                / float(self.ngram_counts[1][(yi_1, yi)])
