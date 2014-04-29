#! /usr/bin/python

import sys
from collections import defaultdict
import math

from count_freqs import simple_conll_corpus_iterator as corpus_iter
from count_freqs import Hmm


"""
Count word frequencies in a data file and rewrite the RARE(freq<5) words to
_RARE_
"""


_RARE_WORD_ = '_RARE_'
reducer = Rewriter()
counter = Hmm(3)


def argmax_e(word):
    def emission_iter(word):
        for e in counter.emission_counts.keys():
            if isinstance(e, tuple) and e[0] == word:
                yield e

    if word not in reducer.wc or reducer.wc[word] < 5:
        word = _RARE_WORD_
    return max(emission_iter(word), key=
            (lambda key: counter.emission_counts[key]))

def y_star(word):
    return argmax_e(word)


def gene_word_iterator(gene_dev_file):
    l = gene_dev_file.readline()
    while l:
        word = l.strip()
        if word:
            yield word
        else:
            yield None
        l = gene_dev_file.readline()

def eval_gene_key(gene_dev_file, output):
    i = 0
    for word in gene_word_iterator(gene_dev_file):
        if word:
            output.write("%s %s\n" % (word, y_star(word)[1]))
        else:
            output.write("\n")
        i = i + 1
        if i % 1000 == 0:
            print i, " lines passed"


class Rewriter():
    """
    Store emissions.
    """
    def __init__(self):
        self.wc = defaultdict(int)

    def _train(self, corpus_iterator):
        """
        Count emission probabilities from a corpus file.
        """
        for w in corpus_iterator:
            if w == (None, None):
                continue
            else:
                self.wc[w[0]] += 1

    def _rewrite(self, corpus_iterator, output):
        for w in corpus_iterator:
            if w == (None, None):
                output.write("\n")
            else:
                word, ne_tag = w
                if self.wc[word] < 5:
                    output.write("%s %s\n" % (_RARE_WORD_, ne_tag))
                else:
                    output.write("%s %s\n" % w)


    def train(self, corpus_file):
        self._train(corpus_iter(corpus_file))

    def write_counts(self, output):
        """
        Writes counts to the output file object.
        Format:

        """
        for word in self.wc:            
            output.write("%s COUNTS %i\n" % (word, self.wc[word]))

    def rewrite(self, input, output):
        """
        Rewrite rare words to _RARE_
        """
        input.seek(0)
        self._rewrite(corpus_iter(input), output)
        input.close()
        output.close()


if __name__ == "__main__":
    try:
        input = file(sys.argv[1], 'r')
    except IOError:
        sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
        sys.exit(1)

    output = file(sys.argv[2], 'w')

    reducer.train(input)
    #reducer.write_counts(sys.stdout)

    tmp_filename = './.tmp.gene.1'

    tmp_file = open(tmp_filename, 'w')
    reducer.rewrite(input, tmp_file)

    tmp_file = open(tmp_filename, 'r')
    counter.train(tmp_file)
    tmp_file.close()

    import os
    os.remove(tmp_filename)

    counter.write_counts(output)
    output.close()

    gene_dev_file = file('./gene.dev', 'r')
    eval_file = file('./gene_dev.p1.out', 'w')
    eval_gene_key(gene_dev_file, eval_file)
    eval_file.close()
