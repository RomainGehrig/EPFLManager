class AliasList(object):
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.edge_id = 0

    def __repr__(self):
        return "<%s>" % str(self)

    def __str__(self):
        return "AliasList: " + str(self.edges.values())

    def add_node(self, node):
        """ Add a node in the graph.
            If already present, fails silently. """
        if node in self.nodes:
            return

        self.nodes[node] = self.edge_id
        self.add_edges(set((node,)))

    def add_edges(self, s):
        if not isinstance(s, set):
            s = set(s)

        self.edges[self.edge_id] = s
        self.edge_id += 1

        return self.edge_id - 1

    def add_and_merge(self, node, to):
        if node in self.nodes:
            return

        to_id = self.nodes[to]
        self.edges[to_id].add(node)
        self.nodes[node] = to_id

    def merge_edges(self, node1, node2):
        node1_id = self.nodes[node1]
        node2_id = self.nodes[node2]

        new_set = self.edges[node1_id] | self.edges[node2_id]

        set_id = self.add_edges(new_set)

        # Update the old nodes
        for n in new_set:
            self.nodes[n] = set_id

        del self.edges[node1_id]
        del self.edges[node2_id]

    def aliases(self, node):
        if node not in self.nodes:
            return set()
        else:
            return self.edges[self.nodes[node]]

    def nodes(self):
        return self.nodes.keys()
