#! /usr/bin/python
"""
Count word frequencies in a data file and replace the RARE(freq<5) words to
RARE_TAG
"""

import sys
from collections import defaultdict
import math
import re

from count_freqs import simple_conll_corpus_iterator as corpus_iter
from count_freqs import Hmm


class SimpleTagger(Hmm):
    """
    Store emissions.
    """

    def __init__(self, n=3):
        super(SimpleTagger, self).__init__(n)

        self.tags = set()
        self.wc = defaultdict(int)
        self.rare_tag = '_RARE_'
        self.rare_threshold = 5

    def count_word(self, corpus_iterator):
        """
        Count emission probabilities from a corpus file.
        """
        for w in corpus_iterator:
            if w == (None, None):
                continue
            else:
                self.wc[w[0]] += 1
                self.tags.add(w[1])

    def group_rare(self, word):
        return self.rare_tag

    def replace_rare_tag(self, corpus_iterator, output):
        """
        Replace rare words to _RARE_
        """
        for w in corpus_iterator:
            if w == (None, None):
                output.write("\n")
            else:
                word, ne_tag = w
                if self.wc[word] < self.rare_threshold:
                    output.write("%s %s\n" % (self.group_rare(word), ne_tag))
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
        def emission_iter(w):
            for e in self.emission_counts.keys():
                if isinstance(e, tuple) and e[0] == w:
                    yield e

        if word not in self.wc or self.wc[word] < self.rare_threshold:
            word = self.group_rare(word)
        return max(emission_iter(word), key=(lambda key: self.e_xy(key[0], key[1])))

    def y_star(self, word):
        return self.argmax_e(word)

    def e_xy(self, x, y):
        if x not in self.wc or self.wc[x] < self.rare_threshold:
            x = self.group_rare(x)
        return float(self.emission_counts[(x, y)]) / float(self.ngram_counts[0][(y,)])


class ViterbiTagger(SimpleTagger):
    def __init__(self, n=3):
        super(ViterbiTagger, self).__init__(n)
        self.pi = defaultdict(float)
        self.pi[(0, '*', '*')] = 1.
        self.bp = defaultdict(float)

    def q(self, yi, yi_2, yi_1):
        return float(self.ngram_counts[2][(yi_2, yi_1, yi)]) / float(
            self.ngram_counts[1][(yi_1, yi)])

    def tag(self, sentence):
        n = len(sentence)
        x = [None]
        x.extend(sentence)

        s = {True: ['*'], False: self.tags}
        y = [''] * (n + 1)

        for k in xrange(1, n + 1):
            for u in s[k - 1 < 1]:
                for v in s[k < 1]:
                    self.bp[(k, u, v)] = max(s[k - 2 < 1], key=lambda w: self.pi[(
                        k - 1, w, u)] * self.q(v, w, u) * self.e_xy(x[k], v))
                    w = self.bp[(k, u, v)]
                    self.pi[(k, u, v)] = self.pi[(k - 1, w, u)] * self.q(
                        v, w, u) * self.e_xy(x[k], v)

        y[n - 1], y[n] = max([(u, v) for u in s[n - 1 < 1] for v in s[n < 1]],
                             key=lambda (u, v): self.pi[(n, u, v)] * self.q('STOP', u, v))
        for k in xrange(n - 2, 0, -1):
            y[k] = self.bp[(k + 2, y[k + 1], y[k + 2])]
        return y[1:]


class ViterbiTaggerEx(ViterbiTagger):
    def __init__(self, n=3):
        super(ViterbiTaggerEx, self).__init__(n)

        self.numeric_tag = '_NUMERIC_'
        self.all_capitals_tag = '_ALL_CAPITALS_'
        self.last_capitals_tag = '_LAST_CAPITALS_'

        self.numeric_pattern = '\d+'
        self.all_capitals_pattern = '^[A-Z]+$'
        self.last_capitals_pattern = '[A-Z]+$'

    def group_rare(self, word):
        def pattern_match(pattern):
            if re.search(pattern, word):
                return True
            return False

        if pattern_match(self.numeric_pattern):
            return self.numeric_tag
        if pattern_match(self.all_capitals_pattern):
            return self.all_capitals_tag
        if pattern_match(self.last_capitals_pattern):
            return self.last_capitals_tag
        return self.rare_tag

