#! /usr/bin/python

import sys
from collections import defaultdict
import math

from count_freqs import simple_conll_corpus_iterator as corpus_iter

"""
Count word frequencies in a data file and rewrite the RARE(freq<5) words to
_RARE_
"""


class Counter():
    """
    Store emissions.
    """

    def __init__(self):
        self.word_counts = defaultdict(int)

    def _train(self, corpus_iterator):
        """
        Count emission probabilities from a corpus file.
        """
        for w in corpus_iterator:
            if w == (None, None):
                continue
            else:
                self.word_counts[w[0]] += 1

    def _rewrite(self, corpus_iterator, output):
        for w in corpus_iterator:
            if w == (None, None):
                output.write("\n")
            else:
                word, ne_tag = w
                if self.word_counts[word] < 5:
                    output.write("_RARE_ %s\n" % ne_tag)
                else:
                    output.write("%s %s\n" % w)


    def train(self, corpus_file):
        self._train(corpus_iter(corpus_file))

    def write_counts(self, output):
        """
        Writes counts to the output file object.
        Format:

        """
        for word in self.word_counts:            
            output.write("%s COUNTS %i\n" % (word, self.word_counts[word]))

    def rewrite(self, corpus_file, output):
        """
        Rewrite rare words to _RARE_
        """
        self._rewrite(corpus_iter(corpus_file), output)
        

if __name__ == "__main__":
    try:
        input = file(sys.argv[1], "r")
    except IOError:
        sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
        sys.exit(1)

    reducer = Counter()
    reducer.train(input)
    #reducer.write_counts(sys.stdout)
    input.seek(0)
    reducer.rewrite(input, sys.stdout)


