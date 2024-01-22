class Predicate:
    # Predicate 是在程序执行过程中，遇到if时候的一种表现
    def __init__(self, st, result):
        # symtype存储的是当前if分支的约束式子
        self.symtype = st
        # result存储的是当前约束在这种变量赋值的情况下的结果
        self.result = result

    def getVars(self):
        # 获得当前if分支约束中的变量
        # (< a#0 0) 中的变量是a， 所以该函数的运行结果会返回a
        return self.symtype.getVars()

    def __eq__(self, other):
        if isinstance(other, Predicate):
            # 判断两个predicate是否相同，取决于两者的结果是否一致，以及表达式是否等价
            # symbolicEq在symbolic_type.py中定义了
            res = self.result == other.result and self.symtype.symbolicEq(other.symtype)
            return res
        else:
            return False

    def __hash__(self):
        return hash(self.symtype)

    def __str__(self):
        return self.symtype.toString() + "(%s)" % (self.result)

    def __repr__(self):
        # 返回一个有效的表达式，用于创建对象的副本
        return self.__str__()

    def negate(self):
        # 将当前的predicate变成相反的逻辑表达式
        assert(self.result is not None)
        self.result = not self.result
