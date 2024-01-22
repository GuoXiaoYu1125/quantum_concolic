from optparse import OptionParser  # 命令行解析库
import os
import sys
from concolic.loader import loaderFactory, generate_quantum_version
from concolic.explore import ExplorationEngine
import time

print("Quantum Concolic with dreal")

# 接受命令行指令
usage = "usage: %prog [options] <path to a *.py file>"
parser = OptionParser(usage=usage)

parser.add_option("-s", "--start", dest="entry", action="store", help="Specify entry point", default="")
parser.add_option("-n", "--number", dest="qbit_num", type="int", help="Circuit qubit number", default=3)
parser.add_option("-m", "--max-iters", dest="max_iters", type="int", help="Run specified number of iterations", default=0)
parser.add_option("-r", "--repeat", dest="repeat_times", type="int", help="Exection repeated times", default=3)

(options, args) = parser.parse_args()

filename = os.path.abspath(args[0])

# 将目标文件转化为Loader，名字为app
# app = loaderFactory(filename, options.entry, options.qbit_num)

new_filename = generate_quantum_version(filename, options.entry)
app = loaderFactory(new_filename, "", options.qbit_num)

if app == None:
    sys.exit(1)

print("Exploring.......................")

result = None

solver = "z3"

try:
    engine = ExplorationEngine(funcinv=app.createInvocation(), solver=solver, repeated_times=options.repeat_times)
    # engine._updateSymbolicParameter("x", 0)
    # engine._updateSymbolicParameter("qc",[(0.651125781587849-0.09097659994144289j), (0.019986152913620502-0.13175366600751648j), (-0.041714839098245665+0.09434689585540013j), (0.38889892898833905-0.6229896937134527j)])
    # engine._oneExecution()

    # 进行concolic的探索过程
    expected_result =  app.get_expected_result()
    engine.expected = expected_result
    start_zeus = time.time()
    generatedInputs, returnVals, path = engine.explore(10)
    result = app.executionComplete(returnVals)
    finish_zeus = time.time()
    print("Finish Time:",finish_zeus-start_zeus)


except ImportError:
    sys.exit(1)

if result is None or result == True:
    sys.exit(0)
else:
    sys.exit(1)
