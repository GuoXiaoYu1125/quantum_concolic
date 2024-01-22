import inspect  # 函数监控器
import os
import sys
import re
from concolic.invocation import FunctionInvocation
from concolic.symbolic_types import SymbolicInteger, getSymbolic, SymbolicCircuit


class Loader:
    # 创建一个文件读取器
    def __init__(self, filename, entry, qbit_num):
        # entry 指的是从哪个函数开始进行执行， 没有指定就默认为文件名的函数
        self._fileName = os.path.basename(filename)
        self._fileName = self._fileName[:-3]
        if (entry == ""):
            self._entryPoint = self._fileName
        else:
            self._entryPoint = entry
        self._resetCallback(True)
        self.qbit_num = qbit_num

    def _resetCallback(self, firstpass=False):
        self.app = None
        if firstpass and self._fileName in sys.modules:
            # 判断是否出现文件重名，和反复读取文件
            print("There already is a module loaded named " + self._fileName)
            raise ImportError()
        try:
            if (not firstpass and self._fileName in sys.modules):
                # 如果不是第一次读取文件，则将该文件删除，从而实现reset
                del (sys.modules[self._fileName])

            # 用__import__ 将文件读入
            self.app = __import__(self._fileName)

            # 如果指定的函数名不存在，或者无法调用，则报错
            if not self._entryPoint in self.app.__dict__ or not callable(self.app.__dict__[self._entryPoint]):
                print("File " + self._fileName + ".py doesn't contain a function named " + self._entryPoint)
                raise ImportError()
        except Exception as arg:
            print("Couldn't import " + self._fileName)
            print(arg)
            raise ImportError()

    def getFile(self):
        return self._fileName

    def getEntry(self):
        return self._entryPoint

    def _execute(self, **args):
        # 将**args字典类型的参数传输给指定的函数对象
        return self.app.__dict__[self._entryPoint](**args)
    
    def get_expected_result(self):
        return self.app.__dict__["expected_result"]()

    def executionComplete(self, return_vals):
        if "expected_result" in self.app.__dict__:
            # 检查输出结果是否都在expected_result函数的输出中
            return self._check(return_vals, self.app.__dict__["expected_result"]())
        if "expected_result_set" in self.app.__dict__:
            return self._check(return_vals, self.app.__dict__["expected_result_set"](), False)
        else:
            print(self._fileName + ".py contains no expected_result function")
            return None

    def _check(self, computed, expected, as_bag=True):
        # computed 和 expected 是两个输出的list
        b_c = self._toBag(computed)
        b_e = self._toBag(expected)
        if as_bag and b_c.keys() != b_e.keys() or not as_bag and set(computed) != set(expected):
            # 判断计算结果和预期输出不完全相同，返回False
            print("-------------------> Target program test failed <---------------------")
            print("Expected: %s, found: %s" % (b_e.keys(), b_c.keys()))
            return False
        else:
            print("Target program test passed <---")
            return True

    def _toBag(self, l):
        # 将列表数据变为字典数据
        bag = {}
        for i in l:
            if i in bag:
                bag[i] += 1
            else:
                bag[i] = 1
        return bag

    def createInvocation(self):
        # 利用读取文件的loader，创建对应的可执行函数
        inv = FunctionInvocation(self._execute, self._resetCallback)
        func = self.app.__dict__[self._entryPoint]

        # 利用函数监控器，获取当前函数的所有可变参数
        argspec = inspect.getfullargspec(func)

        # 通过 @symbolic 和 @concrete 创建的指定类型的参数， 追加检测机制
        if "concrete_args" in func.__dict__:
            for (f, v) in func.concrete_args.items():
                if not f in argspec.args:
                    # 预设变量不存在
                    print("Error in @concrete: " + self._entryPoint + " has no argument named " + f)
                    raise ImportError()
                else:
                    # Loader将用户预设的初始值和初始类型传输给对应的变量
                    Loader._initializeArgumentConcrete(inv, f, v)

        if "symbolic_args" in func.__dict__:
            for (f, v) in func.symbolic_args.items():
                if not f in argspec.args:
                    print("Error (@symbolic): " + self._entryPoint + " has no argument named " + f)
                    raise ImportError()
                elif f in inv.getNames():
                    # 如果f已经被上面的concrete方法赋值过，存在inv的内部，则出现重复赋值的错误
                    print("Argument " + f + " defined in both @concrete and @symbolic")
                    raise ImportError()
                else:
                    # 获取目标初始值的类型
                    s = getSymbolic(v)
                    # 如果不存在相匹配的类型，则报错
                    if (s == None):
                        print(
                            "Error at argument " + f + " of entry point " + self._entryPoint + " : no corresponding symbolic type found for type " + str(
                                type(v)))
                        raise ImportError()
                    # 否则，将对应的值赋值给对应的变量
                    Loader._initializeArgumentSymbolic(inv, f, v, s)

        # 如果对于没有预设类型和初始值的变量
        for a in argspec.args:
            if not a in inv.getNames():
                # 判断当前变量未提前赋值过
                if a == "qc":
                    # 将qc变量视为Symbolic Circuit
                    initial_state = [1] + [0 for i in range(2 ** self.qbit_num - 1)]
                    Loader._initializeArgumentSymbolic(inv, a, initial_state, SymbolicCircuit)
                else:
                    # 除了qc变量以外，都视为整数类型
                    Loader._initializeArgumentSymbolic(inv, a, 0, SymbolicInteger)
        # 返回配置好变量类型和初始值的函数
        return inv

    def _initializeArgumentConcrete(inv, f, val):
        # lambda n,v: val 的意思是，当前的构造器接受n和v两个变量，一定返回val的值
        # def x(n,v):
        #     return val
        # 因为是concrete value，所有无论给什么参数，都只会返回具体的val数值
        inv.addArgumentConstructor(f, val, lambda n, v: val)

    def _initializeArgumentSymbolic(inv, f, val, st):
        # st 是当前符号变量的符号类型
        inv.addArgumentConstructor(f, val, lambda n, v: st(n, v))


def loaderFactory(filename, entry, qbit_num):
    # 在生成loader前的一些预处理
    if not os.path.isfile(filename) or not re.search(".py$", filename):
        print("Please provide a Python file to load")
        return None
    try:
        dir = os.path.dirname(filename)
        sys.path = [dir] + sys.path
        ret = Loader(filename, entry, qbit_num)
        return ret
    except ImportError:
        sys.path = sys.path[1:]
        return None


def generate_quantum_version(filename, entry):
    # 由于QuantumCircuit不存在一些逻辑操作函数，因此无法直接产生对应的逻辑判断和路径约束生成
    # 因此，对于量子程序，我们产生一个新的程序文本，用于理解和生成可执行的动态逻辑路径
    quantum_code = ""
    _fileName = os.path.basename(filename)
    _fileName = _fileName[:-3]
    if (entry == ""):
        _entryPoint = _fileName
    else:
        _entryPoint = entry
    with open(filename, "r") as program_file:
        for line in program_file:
            if _entryPoint in line:
                line = line.replace(_entryPoint, "new_quantum")
            if "check_state_eq" in line and "def" not in line:
                pattern = r"check_state_eq\(([^)]+), \[([^]]+)\], ([^)]+)\)"
                replacement = r"\1.check_state_eq([\2],\3)"
                line = re.sub(pattern, replacement, line)
            if "check_state_gt" in line and "def" not in line:
                line = line.replace("qc, ", "")
                line = line.replace("check_state_gt", "qc.check_state_gt")
            if "check_state_lt" in line and "def" not in line:
                line = line.replace("qc, ", "")
                line = line.replace("check_state_lt", "qc.check_state_lt")
            quantum_code += line
    with open("test/temp_file/new_quantum.py", "w+") as temp_file:
        temp_file.write(quantum_code)
    return "test/temp_file/new_quantum.py"
