import functools
import inspect
import traceback


class SymbolicType(object):
    # 一个抽象的大类，用于产生symbolic execution的symbolic对象
    # 其他的sumbolic对象都需要继承这个大类的性质
    def __init__(self, name, expr=None):
        self.name = name
        self.expr = expr


    def getConcrValue(self):
        # 因为这是一个完全抽象的类，作为其他抽象对象的父类，因此不存在具体值
        # 在其他更加的子类中，还会具体实现这个函数，因此在这里作为未实现
        raise NotImplemented()

    def wrap(conc, sym):
        # 原因和上面的函数一样
        raise NotImplemented()

    def isVariable(self):
        # 如果有表达式，就不是变量
        # 比如： list，set之类的数据结构
        return self.expr == None

    def unwrap(self):
        # 返回的结果是（变量的concrete值， 变量的SymbolicType符号化后的变量）
        if self.isVariable():
            return (self.getConcrValue(), self)
        else:
            return (self.getConcrValue(), self.expr)

    def getVars(self):
        # 获取变量名
        if self.isVariable():
            return [self.name]
        elif isinstance(self.expr, list):
            return self._getVarsLeaves(self.expr)
        else:
            return []


    def _getVarsLeaves(self, l):
        if isinstance(l, list):
            # 使用递归的方法，将list中的所有SymbolicType对象的name都获取
            return functools.reduce(lambda a, x: self._getVarsLeaves(x) + a, l, [])
        elif isinstance(l, SymbolicType):
            return [l.name]
        else:
            return []

    def _do_sexpr(self, args, fun, op, wrap):
        # 这个比较重要！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        # 对于所有参数，如果是SymbolicType，则还原为原本的样子
        unwrapped = [(a.unwrap() if isinstance(a, SymbolicType) else (a,a)) for a in args]

        # 将fun中的每个输入符号，和对应的具体值构建tuple， 存在args中
        args = zip(inspect.getfullargspec(fun).args, [c for (c,s) in unwrapped])

        # concrete就是将对应的变量名和变量值，用字典的形式传入函数
        concrete = fun(**dict([a for a in args]))

        # symbolic是将op和符号化本身组合在一起
        symbolic = [ op ] + [ s for (c,s) in unwrapped]

        # 用wrap将concrete值用symbolic进行符号化
        return wrap(concrete, symbolic)

    def symbolicEq(self, other):
        # 判断两个SymbolicType是否一致
        if not isinstance(other, SymbolicType):
            return False
        if self.isVariable() or other.isVariable():
            return self.name == other.name
        return self._eq_worker(self.expr, other.expr)

    def _eq_worker(self, expr1, expr2):
        # 判断两个非variable的SymbolicType对象是否一致
        if type(expr1) != type(expr2):
            return False
        if isinstance(expr1, list):
            # 用递归法判断list元素是否相同
            return len(expr1) == len(expr2) and\
                type(expr1[0]) == type(expr2[0]) and\
                all([self._eq_worker(x,y) for x,y in zip(expr1[1:], expr2[1:])])
        elif isinstance(expr1, SymbolicType):
            return expr1.name == expr2.name
        else:
            return expr1 == expr2

    def toString(self):
        if self.isVariable():
            if type(self).__name__ == "SymbolicCircuit":
                return self.name + "#" + str(self.state)+"|"
            else:
                return self.name + "#" + str(self.getConcrValue())
        else:
            return self._toString(self.expr)

    def _toString(self, expr):
        if isinstance(expr, list):
            return "(" + expr[0] + " " + ", ".join([self._toString(a) for a in expr[1:]]) + ")"
        elif isinstance(expr, SymbolicType):
            return expr.toString()
        else:
            return str(expr)

class SymbolicObject(SymbolicType, object):
    # 这个类为了记录一些二元逻辑操作 relational comparison operators

    # SI 由 ConcolicEngine 设置，将 __bool__ 与 PathConstraint 连接起来
    # SI 中保存的是一个PathToConstraint的对象
    SI = None

    def __init__(self, name, expr=None):
        SymbolicType.__init__(self,name, expr)

    def wrap(conc, sym):
        raise NotImplemented()

    # 这是一个关键的拦截点：在 Python 执行过程中（if、while、and、or），
    # 只要对谓词进行求值，就会调用 __bool__ 方法。这样我们就可以 捕获路径条件
    # 这个函数非常重要！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
    def __bool__(self):
        # trace = traceback.extract_stack()[-2]
        # print(f"Code:{trace.line}")
        # print(SymbolicObject.SI.expected_path)
        ret = bool(self.getConcrValue())
        if SymbolicObject.SI != None:
            # SI 中保存的是一个PathToConstraint的对象
            SymbolicObject.SI.whichBranch(ret, self)
        return ret

    def _do_bin_op(self, other, fun, op, wrap):
        return self._do_sexpr([self, other], fun, op, wrap)

    def __eq__(self, other):
        # 当SymbolicObject类的对象识别到"=="的时候，执行判断
        return self._do_bin_op(other, lambda x, y: x == y, "==", SymbolicObject.wrap)

    def __ne__(self, other):
        return self._do_bin_op(other, lambda x, y: x != y, "!=", SymbolicObject.wrap)

    def __lt__(self, other):
        return self._do_bin_op(other, lambda x, y: x < y, "<", SymbolicObject.wrap)

    def __le__(self, other):
        return self._do_bin_op(other, lambda x, y: x <= y, "<=", SymbolicObject.wrap)

    def __gt__(self, other):
        return self._do_bin_op(other, lambda x, y: x > y, ">", SymbolicObject.wrap)

    def __ge__(self, other):
        return self._do_bin_op(other, lambda x, y: x >= y, ">=", SymbolicObject.wrap)






