#! /usr/bin/python

import sys
from collections import defaultdict
import math

from count_freqs import simple_conll_corpus_iterator as corpus_iter
from count_freqs import Hmm
from hmm import ViterbiTagger


def gene_word_iterator(input):
    l = input.readline()
    while l:
        word = l.strip()
        if word:
            yield word
        else:
            yield None
        l = input.readline()


def sentence_iterator(corpus_iterator):
    """
    Return an iterator object that yields one sentence at a time.
    """
    current_sentence = []  # Buffer for the current sentence
    for word in corpus_iterator:
        if word is None:
            if current_sentence:  # Reached the end of a sentence
                yield current_sentence
                current_sentence = []  # Reset buffer
            else:  # Got empty input stream
                sys.stderr.write("WARNING: Got empty input file/stream.\n")
                raise StopIteration
        else:
            current_sentence.append(word)  # Add token to the buffer

    if current_sentence:  # If the last line was blank, we're done
        yield current_sentence  # Otherwise when there is no more token
        # in the stream return the last sentence.


def tag(tagger, input, output):
    k = 0
    for sentence in sentence_iterator(gene_word_iterator(input)):
        tags = tagger.tag(sentence)
        for i in xrange(len(tags)):
            output.write("%s %s\n" % (sentence[i], tags[i]))
        output.write("\n")
        k += 1
        if k % 100 == 0:
            print k, " sentence passed"


def train(tagger, train_filename, rare_filename):
    # 1. read train file, count words
    tagger.count_word(corpus_iter(file(train_filename)))

    replace = False
    if replace:
        # 2. replace rare words
        tagger.replace_rare_tag(corpus_iter(file(train_filename)),
                                file(rare_filename, 'w'))

    # 3. read replaced train file, count ngrams
    tagger.train(file(rare_filename))


def main():
    # 1. training
    train_filename = 'gene.train'
    rare_filename = 'gene.train.cats'

    tagger = ViterbiTagger(3)
    train(tagger, train_filename, rare_filename)

    # 2. tagging
    test_filename = 'gene.dev'
    pred_filename = 'gene_dev.p3.out'

    tag(tagger, file(test_filename), file(pred_filename, 'w'))


if __name__ == "__main__":
    main()
