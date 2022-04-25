import itertools
import sys

def arrayToString(s):
    combined = ""
    return combined.join(s)


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
        """
        :type start: int
        :type end: IntPtr
        :rtype: Node
        """
        self.serial = next(self.serial_generator)

        self.value = value

        self.children = {}

        # For root node, suffixLink will be set to NULL.  For internal nodes,
        # suffixLink will be set to root by default in current extension and
        # may change in next extension.

        # Pointer to other node via suffix link
        self.suffixLink = root

        # (start, end) interval specifies the edge, by which the node is
        # connected to its parent node. Each edge will connect two nodes, one
        # parent and one child, and (start, end) interval of a given edge will
        # be stored in the child node. Lets say there are two nods A and B
        # connected by an edge with indices (5, 8) then this indices (5, 8)
        # will be stored in node B.
        self.start = start
        self.end = end

        # suffixIndex will be set to -1 by default and actual suffix index will
        # be set later for leaves at the end of all phases.

        # For leaf nodes, it stores the index of suffix for the path from root
        # to leaf.
        self.suffixIndex = -1

    def __repr__(self):
        return str(self.value)

    def __lt__(self, other):
        return self.value < other.value


class SuffixTree:
    text = []  # self.text to analyze

    class Shared(object):
        root = None  # Pointer to root node

        # lastNewNode will point to newly created internal node, waiting for
        # it's suffix link to be set, which might get a new suffix link (other
        # than root) in next extension of same phase. lastNewNode will be set
        # to NULL when last newly created internal node (if there is any) got
        # it's suffix link reset to new internal node created in next extension
        # of same phase.

        lastNewNode = None
        activeNode = None

        # activeEdge is represeted as input string character index (not the
        # character itself).

        activeEdge = -1
        activeLength = 0

        # remainingSuffixCount tells how many suffixes yet to be added in tree
        remainingSuffixCount = 0
        leafEnd = IntPtr(-1)
        rootEnd = None
        splitEnd = None
        size = -1  # Length of input string

    def edgeLength(self, n):
        """
        :type n: Node
        :rtype: int
        """
        if n == self.Shared.root:
            return 0
        return n.end.get() - n.start + 1

    def walkDown(self, current_node):
        """
        :type current_node: Node
        :rtype: bool
        """
        # Skip/Count Trick
        # (Trick 1). If activeLength is greater than current edge length, set
        # next internal node as activeNode and adjust activeEdge and
        # activeLength accordingly to represent same activePoint.
        if self.Shared.activeLength >= self.edgeLength(current_node):
            self.Shared.activeEdge += self.edgeLength(current_node)
            self.Shared.activeLength -= self.edgeLength(current_node)
            self.Shared.activeNode = current_node
            return True
        else:
            return False

    def extendSuffixTree(self, pos):
        # Extension Rule 1, this takes care of extending all leaves created so
        # far in tree.
        self.Shared.leafEnd.set(pos)

        # Increment remainingSuffixCount indicating that a new suffix added to
        # the list of suffixes yet to be added in tree.
        self.Shared.remainingSuffixCount += 1

        # Set lastNewNode to NULL while starting a new phase, indicating there
        # is no internal node waiting for it's suffix link reset in current
        # phase.
        self.Shared.lastNewNode = None

        # Add all suffixes (yet to be added) one by one in tree
        while self.Shared.remainingSuffixCount > 0:

            if self.Shared.activeLength == 0:
                self.Shared.activeEdge = pos  # APCFALZ

            # There is no outgoing edge starting with activeEdge from
            # activeNode.
            if self.text[self.Shared.activeEdge] not in self.Shared.activeNode.children:
                # Extension Rule 2 (A new leaf edge gets created)
                self.Shared.activeNode.children[self.text[self.Shared.activeEdge]] = \
                    Node(self.Shared.root, pos, self.Shared.leafEnd, self.text[self.Shared.activeEdge])

                # A new leaf edge is created in above line starting from an
                # existng node (the current activeNode), and if there is any
                # internal node waiting for it's suffix link get reset, point
                # the suffix link from that last internal node to current
                # activeNode. Then set lastNewNode to NULL indicating no more
                # node waiting for suffix link reset.
                if self.Shared.lastNewNode:
                    self.Shared.lastNewNode.suffixLink = self.Shared.activeNode
                    self.Shared.lastNewNode = None

            # There is an outgoing edge starting with activeEdge from
            # activeNode.
            else:
                # Get the next node at the end of edge starting with activeEdge
                nxt = self.Shared.activeNode.children[self.text[self.Shared.activeEdge]]
                if self.walkDown(nxt):  # Do self.walkDown
                    # Start from next node (the new activeNode)
                    continue

                # Extension Rule 3 (current character being processed is
                # already on the edge).
                if self.text[nxt.start + self.Shared.activeLength] == self.text[pos]:
                    # If a newly created node waiting for it's suffix link to
                    # be set, then set suffix link of that waiting node to
                    # curent active node.
                    if self.Shared.lastNewNode and self.Shared.activeNode != self.Shared.root:
                        self.Shared.lastNewNode.suffixLink = self.Shared.activeNode
                        self.Shared.lastNewNode = None

                    # APCFER3
                    self.Shared.activeLength += 1
                    # STOP all further processing in this phase and move on to
                    # next phase.
                    break

                # We will be here when activePoint is in middle of the edge
                # being traversed and current character being processed is not
                # on the edge (we fall off the tree). In this case, we add a
                # new internal node and a new leaf edge going out of that new
                # node. This is Extension Rule 2, where a new leaf edge and a
                # new internal node get created.
                self.Shared.splitEnd = IntPtr(nxt.start + self.Shared.activeLength - 1)

                # New internal node
                split = Node(self.Shared.root, nxt.start, self.Shared.splitEnd,
                             self.text[self.Shared.activeEdge])
                self.Shared.activeNode.children[self.text[self.Shared.activeEdge]] = split

                # New leaf coming out of new internal node
                split.children[self.text[pos]] = Node(self.Shared.root, pos, self.Shared.leafEnd,
                                                      self.text[pos])
                nxt.start += self.Shared.activeLength
                split.children[self.text[nxt.start]] = nxt

                # We got a new internal node here. If there is any internal
                # node created in last extensions of same phase which is still
                # waiting for it's suffix link reset, do it now.
                if self.Shared.lastNewNode:
                    # suffixLink of lastNewNode points to current newly created
                    # internal node.
                    self.Shared.lastNewNode.suffixLink = split

                # Make the current newly created internal node waiting for it's
                # suffix link reset (which is pointing to root at present). If
                # we come across any other internal node (existing or newly
                # created) in next extension of same phase, when a new leaf
                # edge gets added (i.e. when Extension Rule 2 applies is any of
                # the next extension of same phase) at that point, suffixLink
                # of this node will point to that internal node.
                self.Shared.lastNewNode = split

            # One suffix got added in tree, decrement the count of
            # suffixes yet to be added.
            self.Shared.remainingSuffixCount -= 1
            if self.Shared.activeNode == self.Shared.root and self.Shared.activeLength > 0:
                self.Shared.activeLength -= 1
                self.Shared.activeEdge = pos - self.Shared.remainingSuffixCount + 1
            elif self.Shared.activeNode != self.Shared.root:
                self.Shared.activeNode = self.Shared.activeNode.suffixLink

    # Print the suffix tree as well along with setting suffix index so tree
    # will be printed in DFS manner.  Each edge along with it's suffix index
    # will be printed.
    def setSuffixIndexByDFS(self, n, label_height):
        if n is None:
            return

        if n.start != -1:  # A non-root node
            pass

        leaf = True
        sorted_children = sorted(n.children.values())
        for child in sorted_children:
            # Current node is not a leaf as it has outgoing
            # edges from it.
            leaf = False

            self.setSuffixIndexByDFS(child, label_height + self.edgeLength(child))

        if leaf:
            n.suffixIndex = self.Shared.size - label_height

    # Build the suffix tree and print the edge labels along with
    # suffixIndex. suffixIndex for leaf edges will be >= 0 and
    # for non-leaf edges will be -1.
    def buildSuffixTree(self):
        self.Shared.size = len(self.text)
        self.Shared.rootEnd = IntPtr(- 1)

        # Root is a special node with start and end indices as -1,
        # as it has no parent from where an edge comes to root.
        self.Shared.root = Node(self.Shared.root, -1, self.Shared.rootEnd)

        self.Shared.activeNode = self.Shared.root  # First activeNode will be root
        for i in range(self.Shared.size):
            self.extendSuffixTree(i)
        labelHeight = 0
        self.setSuffixIndexByDFS(self.Shared.root, labelHeight)

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
        self.buildSuffixTree()

    def getSuffixArray(self):
        array = []
        idxa = IntPtr(0)
        self.buildSuffixArray(self.Shared.root, idxa, array)

# converting 0 index to 1
        #for i in range(len(array)):
            #array[i] += 1

        return array


def BWS(string):
        bws = []
        if string[-1] != '$':
            string += "$"
        print(string)
        suffix_tree = SuffixTree(string)
        suffix_array = suffix_tree.getSuffixArray()
        for i in range(len(suffix_array)):
            index = int(suffix_array[i])-1
            if index == -1:
                index = len(suffix_array)-1
            rotated_value = string[index]
            bws.append(rotated_value)
        return bws


if __name__ == "__main__":
    string_file = sys.argv[1]
    outputFileName = "output_bwt.txt"
    string_input = open(string_file, 'r').readline()
    bws_list = BWS(string_input)
    bws = ''.join(map(str, bws_list))
    output = open(outputFileName, "w")
    output.write(bws)
