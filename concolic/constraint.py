class Constraint:
    # 构建一个约束的树结构，根据路径的差异定义父节点和子节点
    # cnt是一个计数器
    cnt = 0
    def __init__(self, parent, last_predicate, unaccepted_results=[]):
        self.inputs = None
        # 由于求解器求解的结果随机性，以及量子程序的读取随机性，我们构建一个不可接受的状态集合
        self.unaccepted_results = unaccepted_results
        self.predicate = last_predicate
        # processed用于标记当前的约束是否已经被处理
        self.processed = False
        self.parent = parent
        self.children = []
        # 根据节点的创建顺序，赋值给id，用于区分不同的节点
        self.id = self.__class__.cnt
        self.__class__.cnt +=1

    def __eq__(self, other):
        # 两条约束如果相同，有且仅有，两个约束拥有相同的predicates
        if isinstance(other, Constraint):
            if not self.predicate == other.predicate:
                return False
            return self.parent is other.parent
        else:
            return False

    def getAssertsAndQuery(self):
        # 标记为该约束已被处理
        self.processed = True

        # [('a', -16), ('b', 0)]
        # asserts存储的是当前判断节点之前的所有路径结果
        # asserts: [(< a#-16, 0) (True)]
        # self.predicate存储的是当前的变量取值对于判断节点的结果
        # predicate: (== b#0, 16) (False)
        asserts = []
        tmp = self.parent
        while tmp.predicate is not None:
            asserts.append(tmp.predicate)
            tmp = tmp.parent

        return asserts, self.predicate


    def getLength(self):
        if self.parent == None:
            return 0
        return 1 + self.parent.getLength()

    def __str__(self):
        return str(self.predicate) + " (processed: %s, path_len: %d)" % (self.processed, self.getLength())

    def __repr__(self):
        s = repr(self.predicate) + " (processed: %s)" % (self.processed)
        if self.parent is not None:
            s += "\n  path: %s" % repr(self.parent)
        return s


    def findChild(self, predicate):
        # 找出对于当前的predicate结果，符合条件的子节点
        for c in self.children:
            if predicate == c.predicate:
                return c
        return None

    def addChild(self, predicate):
        assert(self.findChild(predicate) is None)
        c = Constraint(self, predicate)
        self.children.append(c)
        return c