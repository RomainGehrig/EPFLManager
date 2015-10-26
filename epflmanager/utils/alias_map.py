class AliasMap(object):
    def __init__(self):
        self._roots = {}
        self._aliases = {}

    def __repr__(self):
        return "<%s>" % str(self)

    def __str__(self):
        return "AliasMap: %s" % self._roots

    def add_root(self, root):
        # If the root already exists, ignore
        if root in self._roots:
            return

        self._roots[root] = set()
        self._aliases[root] = root

    def add_alias(self, alias, of):
        if alias in self._aliases:
            return

        root = self._aliases[of]
        self._aliases[alias] = root

        self._roots[root].add(alias)

    def del_root(self, root):
        # If the root not in existing roots, ignore
        if root not in self._roots:
            return

        aliases = self._roots[root]
        for n in aliases:
            del self._aliases[n]

        del self._roots[root]

    def del_alias(self, alias):
        # TODO: what if alias is a root?
        if alias not in self._aliases:
            return

        if alias in self._roots:
            raise NotImplemented("Deleting an alias that is a root")

        root = self._aliases[alias]
        self._roots[root].remove(alias)
        del self._aliases[alias]

    def get_root(self, alias):
        return self._aliases[alias]

    def are_aliases(self, alias1, alias2):
        return self._aliases[alias1] == self._aliases[alias2]

    def is_root(self, root):
        return root in self._roots
