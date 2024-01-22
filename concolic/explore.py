from collections import deque
from concolic.path_to_constraint import PathToConstraint
from concolic.symbolic_types import symbolic_type
from concolic.symbolic_types import SymbolicType
from quantum_constraint_solver.quantum_solver import quantum_constraint_solver
from concolic.z3_wrap import Z3Wrapper
import random
import re
import time

bin_op = {"==": "!=", "!=": "==", ">": "<", "<": ">"}


class ExplorationEngine:
    def __init__(self, funcinv, solver="z3", repeated_times=10):
        self.invocation = funcinv
        self.symbolic_inputs = {}
        self.repeated_times = repeated_times
        self.expected = None
        for n in funcinv.getNames():
            # 对于函数中每个输入变量，都用对应的构建器产生一个预设值和预设类型
            self.symbolic_inputs[n] = funcinv.createArgumentValue(n)

        self.constraint_to_solve = deque([])
        self.num_processed_constraints = 0

        self.path = PathToConstraint(lambda c: self.addConstraint(c))

        # 设定当前需要探索的路径数值
        symbolic_type.SymbolicObject.SI = self.path

        self.solver = Z3Wrapper()

        # outputs
        self.generated_inputs = []
        self.execution_return_values = []

        # 计时器
        self.start_time = time.time()

    def addConstraint(self, constraint):
        # 该函数的作用：对于每个约束，保存在constraint_to_solve，并且保存产生这个路径的inputs
        self.constraint_to_solve.append(constraint)
        # 由于约束路径是由一次concrete执行产生的，因此需要保存这个产生路径的inputs
        constraint.inputs = self._getInputs()

    def _getInputs(self):
        return self.symbolic_inputs.copy()

    def _setInputs(self, d):
        self.symbolic_inputs = d

    def _getConcrValue(self, v):
        if isinstance(v, SymbolicType):
            return v.getConcrValue()
        else:
            return v

    def _recordInputs(self):
        # 将当前执行的符号参数的数值保存下来
        args = self.symbolic_inputs
        inputs = [(k, self._getConcrValue(args[k])) for k in args]
        self.generated_inputs.append(inputs)
        print(inputs)
        if "qc" in self.symbolic_inputs.keys():
            print("qc-state:", self.symbolic_inputs["qc"].state)

    def _oneExecution(self, expected_path=None):
        self._recordInputs()
        self.path.reset(expected_path)
        
        # 由于量子程序的输出存在概率的差异，以及每次测量都不一致，因此需要多次重复读取
        for exe_num in range(self.repeated_times):
            # 每次执行前，都把量子符号电路中保存的gate操作清空
            if "qc" in self.symbolic_inputs.keys():
                self.symbolic_inputs["qc"].gates = []
            ret = self.invocation.callFunction(self.symbolic_inputs)
            # print("-------------------------------(Result:", ret, ")-------------------------------")
            if ret not in self.execution_return_values:
                # self.execution_return_values.append(ret)
                new_result_time = time.time()
                print("---------------------------(Time:", new_result_time-self.start_time, ")-------------")
                print("-------------------------------(New Result:", ret, ")-------------------------------")
                if expected_path:
                    expected_path.unaccepted_results = []
                break

        # print(ret)
 
        # 每次执行前，都把量子符号电路中保存的gate操作清空
        # if "qc" in self.symbolic_inputs.keys():
        #     self.symbolic_inputs["qc"].gates = []
        # ret = self.invocation.callFunction(self.symbolic_inputs)
        # print(ret)
        self.execution_return_values.append(ret)

    def _isExplorationComplete(self):
        # 判断探索的程度，是否需要探索的路径都被解决
        num_constr = len(self.constraint_to_solve)
        if num_constr == 0:
            return True
        else:
            return False

    def _updateSymbolicParameter(self, name, val):
        self.symbolic_inputs[name] = self.invocation.createArgumentValue(name, val)

    def explore(self, max_iterations=0):
        # 首先先动态执行一次，从而获取这次执行路径上的约束条件
        self._oneExecution()

        iterations = 1
        if max_iterations != 0 and iterations >= max_iterations:
            return self.execution_return_values

        # 未能获取所有的结果的情况下，重复路径的探索与生成
        while not self._isExplorationComplete():
            # 获取当前的路径约束
            selected = self.constraint_to_solve.popleft()

            # print("explore.py:", selected)

            # 如果当前的路径约束已经被解决，则无视
            if selected.processed:
                continue
            # 否则，将预设的变量值赋给每个变量
            self._setInputs(selected.inputs)

            # 获取当前路径该节点以上的所有约束，保证不变，存储在asserts中
            # 获取当前节点的约束，存储在query中
            # 目标是保证该节点之前的约束不发生改变，只修改当前节点的约束
            asserts, query = selected.getAssertsAndQuery()

            if query.getVars() == ["qc"]:
                qc_constraint = str(query)
                # quantum concolic by symQV part
                # flag, gates, target_prob = process_qc_constraint(qc_constraint)
                # # print("explore.py Now we use quantum solver!!!!!!!!!!!")
                # result, time, result_dict = quantum_constraint_solver(self.symbolic_inputs["qc"].qubits_num, \
                #                                   gates, \
                #                                   target_prob, \
                #                                   flag, \
                #                                   unaccepted_results=selected.unaccepted_results)
                # selected.unaccepted_results.append(result_dict)
                # print("Now we finish the solver!!!!!!!!!!!!!!!")

                # random concolic vector generator
                state_num = pow(2, self.symbolic_inputs["qc"].qubits_num)
                complex_num = [complex(random.uniform(-1, 1), random.uniform(-1, 1)) for i in range(state_num)]
                abs_complex = [abs(i) for i in complex_num]
                result = [i / sum(abs_complex) for i in complex_num]
                model = {"qc": result}
            else:
                model = self.solver.findCounterexample(asserts, query)

            if model == None:
                continue
            else:
                for name in model.keys():
                    self._updateSymbolicParameter(name, model[name])
            
            self._oneExecution(expected_path=selected)
            iterations += 1

            self.num_processed_constraints += 1

            if set(self.execution_return_values) == set(self.expected):
                break

            if max_iterations != 0 and iterations >= max_iterations:
                break

        return self.generated_inputs, self.execution_return_values, self.path


def process_qc_constraint(qc_constraint):
    if "False" in qc_constraint:
        flag = qc_constraint.split("{")[0][1:]
    else:
        flag = bin_op[qc_constraint.split("{")[0][1:]]


    if flag == "==" or flag == "!=":
        matches = re.findall(r'\[[^\]]*\]', qc_constraint)
        gates = eval(matches[0])
        target_prob = eval(matches[-1])
    elif flag == ">" or flag == "<":
        matches = re.findall(r'\[[^\]]*\]', qc_constraint)
        gates = eval(matches[0])
        target_prob = []
        for i in matches[2:]:
            i = i.replace("[[", "[")
            target_prob.append(eval(i))
    return flag, gates, target_prob
