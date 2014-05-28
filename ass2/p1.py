__author__ = 'anakin'

import json
from count_cfg_freq import Counts


class Tagger(Counts):
    """
    Store emissions.
    """
    def __init__(self):
        Counts.__init__(self)

        self.wc = {}
        self.rare_tag = '_RARE_'
        self.rare_threshold = 5

    def count_word(self):
        """
        Count emission probabilities from a corpus file.
        """
        for (_, word), count in self.unary.iteritems():
            if word not in self.wc:
                self.wc.setdefault(word, 0)
            self.wc[word] += count

    def group_rare(self, word):
        return self.rare_tag

    def replace_rare_tag(self, l):
        """
        Replace rare words to _RARE_
        """
        j = json.loads(l)
        self.replace(j)
        return json.dumps(j)

    def replace(self, tree):
        if isinstance(tree, basestring):
            return

        if len(tree) == 3:
            # It is a binary rule.
            # Recursively count the children.
            self.replace(tree[1])
            self.replace(tree[2])
        elif len(tree) == 2:
            # It is a unary rule.
            word = tree[1]
            if word not in self.wc or self.wc[word] < self.rare_threshold:
                tree[1] = self.rare_tag

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

