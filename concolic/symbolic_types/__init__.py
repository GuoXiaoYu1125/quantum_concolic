from concolic.symbolic_types.symbolic_type import SymbolicType as SymType
from concolic.symbolic_types.symbolic_int import SymbolicInteger as SymInt
from concolic.symbolic_types.symbolic_type import SymbolicObject as SymObj
from concolic.symbolic_types.symbolic_circuit import SymbolicCircuit as SymCir
from qiskit import QuantumCircuit

# 保证一些数字参数在面对与符号变量进行二元操作时，会被识别为相同类型
# 否则，会出现类型不匹配，从而报错
SymObj.wrap = lambda conc, sym : SymbolicInteger("se",conc,sym)


SymbolicCircuit = SymCir
SymbolicType = SymType
SymbolicInteger = SymInt

def getSymbolic(v):
	exported = [(int,SymbolicInteger), (QuantumCircuit, SymbolicCircuit)]
	for (t,s) in exported:
		if isinstance(v,t):
			return s
	return None