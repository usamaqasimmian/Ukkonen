import itertools
import sys


def chararray_to_string(s):
    # initialization of string to ""
    new = ""

    # traverse in the string 
    for x in s:
        new += x

        # return string
    return new


class IntPtr(object):
    def __init__(self, i):
        self.i = i

    def get(self):
        return self.i

    def set(self, i):
        self.i = i


class Node(object):
    serial_generator = itertools.count(0)

    def __init__(self, root, start, end, value=None):
        self.serial = next(self.serial_generator)

        self.value = value

        self.children = {}

        # For the root node, suffixLink will be set to None.  For internal nodes,
        # suffixLink will be set to root by default

        # suffix link pointer to the root
        self.suffixLink = root

        self.start = start
        self.end = end

        # suffixIndex will be set to -1 by default and actual suffix index will
        # be set later for leaves at the end of all phases.

        # For leaf nodes, it stores the index of suffix for the path from root to leaf.
        self.suffixIndex = -1

    def __repr__(self):
        return str(self.value)

    def __lt__(self, other):
        return self.value < other.value


class suffix_tree():
    text = []  # self.text to analyze

    class Glob(object):
        root = None  # Pointer to root node

        # lastNewNode will point to newly created internal node, waiting for
        # it's suffix link to be set, which might get a new suffix link (other
        # than root) in next extension of same phase. lastNewNode will be set
        # to NULL when last newly created internal node (if there is any) got
        # it's suffix link reset to new internal node created in next extension
        # of same phase.

        lastNewNode = None
        activeNode = None

        activeEdge = -1
        activeLength = 0

        # remaining stores the number of  suffixes yet to be added to the tree
        remaining = 0
        leafEnd = IntPtr(-1)
        rootEnd = None
        splitEnd = None
        size = -1  # Length of the input string

    def edgeLength(self, n):
        if n == self.Glob.root:
            return 0
        return n.end.get() - n.start + 1

    def walkDown(self, currNode):

        # Skip/Count Trick
        # If activeLength is greater than current edge length, set
        # next internal node as activeNode and adjust activeEdge and
        # activeLength accordingly to represent same activePoint.
        if self.Glob.activeLength >= self.edgeLength(currNode):
            self.Glob.activeEdge += self.edgeLength(currNode)
            self.Glob.activeLength -= self.edgeLength(currNode)
            self.Glob.activeNode = currNode
            return True
        else:
            return False

    def extendSuffixTree(self, pos):
        """
        :type pos: int
        """
        # Extension Rule 1, this takes care of extending all leaves created so far.
        self.Glob.leafEnd.set(pos)

        # Increment remainingSuffixCount indicating that a new suffix added to
        # the list of suffixes yet to be added in tree.
        self.Glob.remaining += 1

        # Set lastNewNode to NULL while starting a new phase, indicating there
        # is no internal node waiting for it's suffix link reset in current
        # phase.
        self.Glob.lastNewNode = None

        # Add all suffixes (yet to be added) one by one in tree
        while self.Glob.remaining > 0:

            if self.Glob.activeLength == 0:
                self.Glob.activeEdge = pos  # APCFALZ

            # There is no outgoing edge starting with activeEdge from
            # activeNode.
            if self.text[self.Glob.activeEdge] not in self.Glob.activeNode.children:
                # Extension Rule 2 (A new leaf edge gets created)
                self.Glob.activeNode.children[self.text[self.Glob.activeEdge]] = \
                    Node(self.Glob.root, pos, self.Glob.leafEnd, self.text[self.Glob.activeEdge])

                # A new leaf edge is created in above line starting from an
                # existng node (the current activeNode), and if there is any
                # internal node waiting for it's suffix link get reset, point
                # the suffix link from that last internal node to current
                # activeNode. Then set lastNewNode to NULL indicating no more
                # node waiting for suffix link reset.
                if self.Glob.lastNewNode:
                    self.Glob.lastNewNode.suffixLink = self.Glob.activeNode
                    self.Glob.lastNewNode = None

            # There is an outgoing edge starting with activeEdge from
            # activeNode.
            else:
                # Get the next node at the end of edge starting with activeEdge
                nxt = self.Glob.activeNode.children[self.text[self.Glob.activeEdge]]
                if self.walkDown(nxt):  # Do self.walkDown
                    # Start from next node (the new activeNode)
                    continue

                # Extension Rule 3 (current character being processed is
                # already on the edge).
                if self.text[nxt.start + self.Glob.activeLength] == self.text[pos]:
                    # If a newly created node waiting for it's suffix link to
                    # be set, then set suffix link of that waiting node to
                    # curent active node.
                    if self.Glob.lastNewNode and self.Glob.activeNode != self.Glob.root:
                        self.Glob.lastNewNode.suffixLink = self.Glob.activeNode
                        self.Glob.lastNewNode = None

                    # APCFER3
                    self.Glob.activeLength += 1
                    # STOP all further processing in this phase and move on to
                    # next phase.
                    break

                # We will be here when activePoint is in middle of the edge
                # being traversed and current character being processed is not
                # on the edge (we fall off the tree). In this case, we add a
                # new internal node and a new leaf edge going out of that new
                # node. This is Extension Rule 2, where a new leaf edge and a
                # new internal node get created.
                self.Glob.splitEnd = IntPtr(nxt.start + self.Glob.activeLength - 1)

                # New internal node
                split = Node(self.Glob.root, nxt.start, self.Glob.splitEnd, self.text[self.Glob.activeEdge])
                self.Glob.activeNode.children[self.text[self.Glob.activeEdge]] = split

                # New leaf coming out of new internal node
                split.children[self.text[pos]] = Node(self.Glob.root, pos, self.Glob.leafEnd, self.text[pos])
                nxt.start += self.Glob.activeLength
                split.children[self.text[nxt.start]] = nxt

                # We got a new internal node here. If there is any internal
                # node created in last extensions of same phase which is still
                # waiting for it's suffix link reset, do it now.
                if self.Glob.lastNewNode:
                    # suffixLink of lastNewNode points to current newly created
                    # internal node.
                    self.Glob.lastNewNode.suffixLink = split

                # Make the current newly created internal node waiting for it's
                # suffix link reset (which is pointing to root at present). If
                # we come across any other internal node (existing or newly
                # created) in next extension of same phase, when a new leaf
                # edge gets added (i.e. when Extension Rule 2 applies is any of
                # the next extension of same phase) at that point, suffixLink
                # of this node will point to that internal node.
                self.Glob.lastNewNode = split

            # One suffix got added in tree, decrement the count of
            # suffixes yet to be added.
            self.Glob.remaining -= 1
            if self.Glob.activeNode == self.Glob.root and self.Glob.activeLength > 0:
                # APCFER2C1
                self.Glob.activeLength -= 1
                self.Glob.activeEdge = pos - self.Glob.remaining + 1
            elif self.Glob.activeNode != self.Glob.root:
                # APCFER2C2
                self.Glob.activeNode = self.Glob.activeNode.suffixLink

    # Print the suffix tree as well along with setting suffix index so tree
    # will be printed in DFS manner.  Each edge along with it's suffix index
    # will be printed.
    def setSuffixIndexByDFS(self, n, labelHeight):
        """
        :type n: Node
        :type labelHeight: int
        """
        if n is None:
            return

        if n.start != -1:  # A non-root node
            # Print the label on edge from parent to current node.  Uncomment
            # below line to print suffix tree.
            # TODO: print_range(n.start, n.end.get()).
            pass

        leaf = True
        for child in sorted(n.children.values()):
            # Current node is not a leaf as it has outgoing
            # edges from it.
            leaf = False

            self.setSuffixIndexByDFS(child, labelHeight + self.edgeLength(child))

        if leaf:
            n.suffixIndex = self.Glob.size - labelHeight

    # Build the suffix tree and print the edge labels along with
    # suffixIndex. suffixIndex for leaf edges will be >= 0 and
    # for non-leaf edges will be -1.
    def buildSuffixTree(self):
        self.Glob.size = len(self.text)
        self.Glob.rootEnd = IntPtr(- 1)

        # Root is a special node with start and end indices as -1,
        # as it has no parent from where an edge comes to root.
        self.Glob.root = Node(self.Glob.root, -1, self.Glob.rootEnd)

        self.Glob.activeNode = self.Glob.root  # First activeNode will be root
        for i in range(self.Glob.size):
            self.extendSuffixTree(i)
        labelHeight = 0
        self.setSuffixIndexByDFS(self.Glob.root, labelHeight)

    def buildSuffixArray(self, curNode, idxa, array):
        if curNode is None:
            return

        if curNode.suffixIndex == -1:  # If it is internal node
            for childkey in sorted(curNode.children.keys()):
                self.buildSuffixArray(curNode.children[childkey], idxa, array)

        # Ignore leaf nodes
        elif curNode.suffixIndex > -1:
            array.insert(idxa.get(), curNode.suffixIndex)
            idxa.set(idxa.get() + 1)

    def __init__(self, string):

        self.text = string
        # adding $ if not present
        if self.text[-1] != '$':
            self.text += "$"

        # Build the Suffix Tree using Ukkonnen's  algorithm
        self.buildSuffixTree()

    def getSuffixArray(self):
        array = []
        idxa = IntPtr(0)
        self.buildSuffixArray(self.Glob.root, idxa, array)
        return array

    def searchPattern(self, pattern):
        # search pat in suffix tree
        matches = []

        def dfs(curNode, indexOfPattern, sols):
            if curNode is None:
                return

            lenOfEdge = self.edgeLength(curNode)
            for id in range(curNode.start, curNode.start + lenOfEdge):
                if indexOfPattern < len(pattern) and pattern[indexOfPattern] != '?' and pattern[indexOfPattern] != \
                        self.text[id]:
                    return
                indexOfPattern += 1

            if curNode.suffixIndex == -1:  # If it is internal node
                for childKey in curNode.children.keys():
                    dfs(curNode.children[childKey], indexOfPattern, sols)

            # Ignore leaf nodes
            elif curNode.suffixIndex > -1:
                if indexOfPattern >= len(pattern):
                    sols.append(curNode.suffixIndex + 1)

        dfs(self.Glob.root, 0, matches)
        return sorted(matches)


if __name__ == "__main__":
    textFileName = sys.argv[1]
    patternFileName = sys.argv[2]
    outputFileName = "output_wild_matching.txt"

    with open(textFileName) as f:
        text = "\n".join(f.readlines())

    with open(patternFileName) as f:
        pat = "\n".join(f.readlines())

    suffixTree = suffix_tree(text)
    print(text, pat)
    pat = suffixTree.searchPattern(pat)
    with open(outputFileName, 'w') as w:
        w.write("\n".join(map(str, pat)))
