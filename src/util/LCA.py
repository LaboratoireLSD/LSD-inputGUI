"""
.. module:: LCA

.. codeauthor:: ?

:Created on: ?

"""
#import unittest,random
#from UnionFind import UnionFind
#from sets import Set

# maintain Python 2.2 compatibility
if 'True' not in globals():
    globals()['True'] = not None
    globals()['False'] = not True

class RestrictedRangeMin:
    """Linear-space RangeMin for integer data obeying the constraint
        abs(X[i]-X[i-1])==1.
        
    We don't actually check this constraint, but results may be incorrect
    if it is violated.  For the use of this data structure from LCA, the
    data are actually pairs rather than integers, but the minima of
    all ranges are in the same positions as the minima of the integers
    in the first positions of each pair, so the data structure still works.
    """
    def __init__(self, X):
        # Compute parameters for partition into blocks.
        # Position i in X becomes transformed into
        # position i&self._blockmask in block i>>self.blocklen
        self._blocksize = _log2(len(X))//2
        self._blockmask = (1 << self._blocksize) - 1
        blocklen = 1 << self._blocksize

        # Do partition into blocks, find minima within
        # each block, prefix minima in each block,
        # and suffix minima in each block
        blocks = []             # map block to block id
        ids = {}                # map block id to PrecomputedRangeMin
        blockmin = []           # map block to min value
        self._prefix = [None]   # map data index to prefix min of block
        self._suffix = []       # map data index to suffix min of block
        for i in range(0, len(X), blocklen):
            XX = X[i:i+blocklen]
            blockmin.append(min(XX))
            self._prefix += PrefixMinima(XX)
            self._suffix += PrefixMinima(XX, isReversed=True)
            blockid = len(XX) < blocklen and -1 or self._blockid(XX)
            blocks.append(blockid)
            if blockid not in ids:
                ids[blockid] = PrecomputedRangeMin(_pairs(XX))
        self._blocks = [ids[b] for b in blocks]

        # Build data structure for interblock queries
        self._blockrange = LogarithmicRangeMin(blockmin)
        self._data = list(X)

    def __getitem__(self, left, right=0):
        if isinstance(left, slice):
            right = left.stop
            left =left.start
        firstblock = left >> self._blocksize
        lastblock = (right - 1) >> self._blocksize
        if firstblock == lastblock:
            i = left & self._blockmask
            position = self._blocks[firstblock][i:i+right-left][1]
            return self._data[position + (firstblock << self._blocksize)]
        else:
            best = min(self._suffix[left], self._prefix[right])
            if lastblock > firstblock + 1:
                best = min(best, self._blockrange[firstblock+1:lastblock])
            return best

    def _blockid(self, XX):
        """Return value such that all blocks with the same
        pattern of increments and decrements get the same id.
        """
        blockid = 0
        for i in range(1, len(XX)):
            blockid = blockid*2 + (XX[i] > XX[i-1])
        return blockid

class PrecomputedRangeMin:
    """RangeMin solved in quadratic space by precomputing all solutions."""

    def __init__(self,X):
        self._minima = [PrefixMinima(X[i:]) for i in range(len(X))]

    def __getitem__(self, x, y=0):
        if isinstance(x, slice):
            y = x.stop
            x =x.start
        return self._minima[x][y-x-1]

    def __len__(self):
        return len(self._minima)

class LogarithmicRangeMin:
    """RangeMin in O(n log n) space and constant query time."""

    def __init__(self,X):
        """Compute min(X[i:i+2**j]) for each possible i,j."""
        self._minima = m = [list(X)]
        for j in range(_log2(len(X))):
            m.append(list(map(min, m[-1], m[-1][1<<j:])))

    def __getitem__(self, x, y=0):
        """Find range minimum by representing range as the union
        of two overlapping subranges with power-of-two lengths.
        """
        if isinstance(x, slice):
            y = x.stop
            x = x.start
        j = _logtable[y-x]
        row = self._minima[j]
        return min(row[x], row[y-2**j])

    def __len__(self):
        return len(self._minima[0])

class LCA:
    """Structure for finding least common ancestors in trees.
    Tree nodes may be any hashable objects; a tree is specified
    by a dictionary mapping nodes to their parents.
    LCA(T)(x,y) finds the LCA of nodes x and y in tree T.
    """
    def __init__(self, parent, RangeMinFactory=RestrictedRangeMin):
        """Construct LCA structure from tree parent relation."""
        children = {}
        for x in parent:
            children.setdefault(parent[x], []).append(x)
        root = [x for x in children if x not in parent]
        if len(root) != 1:
            raise ValueError("LCA input is not a tree")

        levels = []
        self._representatives = {}
        self._visit(children, levels, root[0], 0)
        if [x for x in parent if x not in self._representatives]:
            raise ValueError("LCA input is not a tree")
        self._rangemin = RangeMinFactory(levels)

    def __call__(self, *nodes):
        """Find least common ancestor of a set of nodes."""
        r = [self._representatives[x] for x in nodes]
        return self._rangemin[min(r):max(r)+1][1]

    def _visit(self,children, levels, node, level):
        """Perform Euler traversal of tree."""
        self._representatives[node] = len(levels)
        pair = (level,node)
        levels.append(pair)
        for child in children.get(node, []):
            self._visit(children, levels, child, level+1)
            levels.append(pair)

    def traverse(self, node):
        """Perform depth first traversal of tree."""
        self.ancestors[self.descendants[node]] = node
        for child in self.children.get(node, []):
            self.traverse(child)
            self.descendants.union(child, node)
            self.ancestors[self.descendants[node]] = node
        self.visited.add(node)
        for query in self[node]:
            if query in self.visited:
                lca = self.ancestors[self.descendants[query]]
                self[node][query] = self[query][node] = lca

# Various utility functions

def PrefixMinima(X, isReversed=False):
    """Compute table of prefix minima
    (or suffix minima, if isReversed=True) of list X.
    """
    current = None
    output = [None] * len(X)
    for x, i in _pairs(X, isReversed):
        if current is None:
            current = x
        else:
            current = min(current, x)
        output[i] = current
    return output

def _pairs(X, isReversed=False):
    """Return pairs (x,i) for x in list X, where i is
    the index of x in the data, in forward or reverse order.
    """
    indices = range(len(X))
    if isReversed:
        reversed(indices)
    return [(X[i], i) for i in indices]

_logtable = [None, 0]
def _log2(n):
    """Make table of logs reach up to n and return floor(log_2(n))."""
    while len(_logtable) <= n:
        _logtable.extend([1+_logtable[-1]]*len(_logtable))
    return _logtable[n]
