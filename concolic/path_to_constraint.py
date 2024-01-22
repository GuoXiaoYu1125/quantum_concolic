from concolic.constraint import Constraint
from concolic.predicate import Predicate


class PathToConstraint:
    # 构建路径约束
    def __init__(self, add):
        self.constraint = {}
        # add 本质上是一个约束生成函数， 对应到上层函数是
        # lambda c: self.addConstraint(c)
        # 也就是，add是一个生成器
        # def x(c):
        #     return self.addConstraint(c)
        self.add = add
        # 创建一个根节点的约束点
        self.root_constraint = Constraint(None, None)
        self.current_constraint = self.root_constraint
        # expected_path中存储的是到达预设路径点的所有constraint node的predicate
        self.expected_path = None

    def reset(self, expected):
        # 输入expected是一个Constraint类的对象
        # 重置当前路径，如果有expected对象，就将路径转化为可以到达expected节点的路径
        self.current_constraint = self.root_constraint
        if expected == None:
            self.expected_path = None
        else:
            self.expected_path = []
            tmp = expected
            while tmp.predicate is not None:
                self.expected_path.append(tmp.predicate)
                tmp = tmp.parent

    def whichBranch(self, branch, symbolic_type):
        # 利用symbolic_type和计算结果branch，构建一个Predica对象
        p = Predicate(symbolic_type, branch)
        # 将当前路径取反，变成另一条路径
        p.negate()
        cneg = self.current_constraint.findChild(p)
        p.negate()
        c = self.current_constraint.findChild(p)
        # 上面找出关于当前约束路径的两个子节点c， cneg

        if c is None:
            # 如果c没有出现在约束树上，则追加该节点
            c = self.current_constraint.addChild(p)
            # 对c用约束生成器，转化为约束
            self.add(c)

        if self.expected_path != None and self.expected_path != []:
            # 这部分的判断逻辑是：
            # 由于有预设的expeced节点，所以路径的探索必须到达该节点，如果不是，则认为mismatch
            expected = self.expected_path.pop()
            # done判断当前的路径是否已经取空
            done = self.expected_path == []
            # if (not done and expected.result != c.predicate.result or \
            #     done and expected.result == c.predicate.result):
            #     print("Replay mismatch (done=", done, ")")
            #     print(expected)
            #     print(c.predicate)

        if cneg is not None:
            # 如果已经构建了cneg的节点，上面也已经处理了c的节点
            # 则意味着，该节点的两个子节点都已经被覆盖过了
            cneg.processed = True
            c.processed = True

        # 锁定当前的约束节点目标为c
        self.current_constraint = c








