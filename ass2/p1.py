from collections import defaultdict

__author__ = 'anakin'

import json
from count_cfg_freq import Counts


class Tagger(Counts):
    def __init__(self):
        Counts.__init__(self)

        self.wc = defaultdict(int)
        self.rare_tag = '_RARE_'
        self.rare_threshold = 5

    def count_word(self):
        """
        Count emission probabilities from a corpus file.
        """
        for (_, word), count in self.unary.iteritems():
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
            if self.is_rare_word(tree[1]):
                tree[1] = self.rare_tag

    def is_rare_word(self, word):
        return word not in self.wc or self.wc[word] < self.rare_threshold


class Parser(Tagger):
    def __init__(self):
        Tagger.__init__(self)
        self.pi = defaultdict(float)

    def count_x(self, x):
        return self.nonterm[x]

    def count_x_w(self, x, w):
        if self.is_rare_word(w):
            if (x, self.rare_tag) not in self.unary:
                return 0
            return self.unary[(x, self.rare_tag)]
        if (x, w) not in self.unary:
            return 0
        return self.unary[(x, w)]

    def count_x_yy(self, x, y1, y2):
        if (x, y1, y2) not in self.binary:
            return 0
        return self.binary[(x, y1, y2)]

    def q_x_w(self, x, w):
        return float(self.count_x_w(x, w)) / float(self.count_x(x))

    def q_x_yy(self, x, y1, y2):
        return float(self.count_x_yy(x, y1, y2)) / float(self.count_x(x))

    def parser(self, sentence):
        n = len(sentence)
        '''
        for i in xrange(0, n):
            if self.is_rare_word(sentence[i]):
                sentence[i] = self.rare_tag

        print sentence
                '''

        w = [None]
        w.extend(sentence)
        pi = defaultdict(float)
        bp = defaultdict(float)
        for i in xrange(1, n+1):
            for x in self.nonterm:
                pi[(i, i, x)] = self.q_x_w(x, w[i])

        for l in xrange(1, n):
            for i in xrange(1, n):
                j = i + l
                for x in self.nonterm:
                    t = [(y, z, s) for s in xrange(i, j) for (xp, y, z) in self.binary if xp == x]
                    if t:
                        bp[(i, j, x)] = max(t, key=lambda (y, z, s): self.q_x_yy(x, y, z) * pi[(i, s, y)] * pi[(s+1, j, z)])
                        (y, z, s) = bp[(i, j, x)]
                        pi[(i, j, x)] = self.q_x_yy(x, y, z) * pi[(i, s, y)] * pi[(s+1, j, z)]

        return self.build_tree(1, n, 'SBARQ', w, bp)

    def build_tree(self, start, end, tag, words, bp):
        tree = list()
        tree.append(tag)
        if start == end:
            tree.append(words[start])
        else:
            y1, y2, mid = bp[(start, end, tag)]
            tree.append(self.build_tree(start, mid, y1, words, bp))
            tree.append(self.build_tree(mid+1, end, y2, words, bp))

        return tree

