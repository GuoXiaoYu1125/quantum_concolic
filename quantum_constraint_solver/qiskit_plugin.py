from quantum_constraint_solver.symqv.operations.gates import I, X, Peres, Peres_inv, Y, Z, H, CNOT, SWAP, CZ, T, S, \
    CCX, CCZ, CSWAP, V, V_dag, CV, CV_inv, Rx, Ry, Rz, P, R, ISWAP, U3
import re
from quantum_constraint_solver.symqv.expressions.qbit import Qbits


def args_split(args_string):
    match = re.match(r'(.*)\[(.*)\](.*)', args_string)
    if match:
        before_brackets = match.group(1).replace(",", "")
        inside_brackets = match.group(2).split(",")
        after_brackets = match.group(3).replace(",", "")
        return True, before_brackets, inside_brackets, after_brackets
    else:
        return False, args_string.split(","), None, None


def operation_to_method(num_qbits, operation):
    qbit_name = [f"q{num_qbits-1-i}" for i in range(num_qbits)]
    symqbit = Qbits(qbit_name)
    matches = re.findall(r'\((.*?)\)|([^()]+)', operation)
    gate = [match[0] if match[0] else match[1] for match in matches]
    gate_name, gate_args = gate[0], gate[1]

    if gate_name == "h":
        target = symqbit[int(gate_args[0])]
        return H(target)

    if gate_name == "x":
        target = symqbit[int(gate_args[0])]
        return X(target)

    if gate_name == "ccx":
        args=gate_args.split(",")
        target1, target2, target3 = symqbit[int(args[0])], symqbit[int(args[1])], symqbit[int(args[2])]
        return CCX(target1,target2,target3)

    if gate_name == "ccz":
        args=gate_args.split(",")
        target1, target2, target3 = symqbit[int(args[0])], symqbit[int(args[1])], symqbit[int(args[2])]
        return CCZ(target1,target2,target3)

    if gate_name == "s":
        target = symqbit[int(gate_args[0])]
        return S(target)

    if gate_name == "z":
        target = symqbit[int(gate_args[0])]
        return Z(target)

    if gate_name == "y":
        target = symqbit[int(gate_args[0])]
        return Y(target)

    if gate_name == "sdg":
        target = symqbit[int(gate_args[0])]
        return P(target,-(3.1415926/2))

    if gate_name == "t":
        target = symqbit[int(gate_args[0])]
        return T(target)

    if gate_name == "tdg":
        target = symqbit[int(gate_args[0])]
        return P(target,-(3.1415926/4))

    if gate_name == "ch":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            target = symqbit[int(args1[1])]
            control = symqbit[int(args1[0])]
        return H(target).controlled_by(control)

    if gate_name == "cx" or gate_name == "cnot":
        arg1, arg2 = gate_args.split(",")
        control, target = symqbit[int(arg1)], symqbit[int(arg2)]
        return CNOT(control, target)

    if gate_name == "cs":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            target = symqbit[int(args1[1])]
            control = symqbit[int(args1[0])]
        return S(target).controlled_by(control)

    if gate_name == "cz":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            target = symqbit[int(args1[1])]
            control = symqbit[int(args1[0])]
        return CZ(target,control)

    if gate_name == "csdg":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            target = symqbit[int(args1[1])]
            control = symqbit[int(args1[0])]
        return P(target,-(3.1415926/2)).controlled_by(control)

    if gate_name == "p":
        gate_args = gate_args.split(",")
        theta, target = float(gate_args[0]), symqbit[int(gate_args[1])]
        return P(target,theta)

    if gate_name == "cp":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            theta = float(args1)
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            theta = float(args1[0])
            target = symqbit[int(args1[2])]
            control = symqbit[int(args1[1])]
        return P(target,theta).controlled_by(control)

    if gate_name == "rx":
        gate_args = gate_args.split(",")
        theta, target = float(gate_args[0]), symqbit[int(gate_args[1])]
        return Rx(target,theta)

    if gate_name == "crx":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            theta = float(args1)
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            theta = float(args1[0])
            target = symqbit[int(args1[2])]
            control = symqbit[int(args1[1])]
        return Rx(target,theta).controlled_by(control)

    if gate_name == "ry":
        gate_args = gate_args.split(",")
        theta, target = float(gate_args[0]), symqbit[int(gate_args[1])]
        return Ry(target,theta)

    if gate_name == "cry":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            theta = float(args1)
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            theta = float(args1[0])
            target = symqbit[int(args1[2])]
            control = symqbit[int(args1[1])]
        return Ry(target,theta).controlled_by(control)

    if gate_name == "rz":
        gate_args = gate_args.split(",")
        theta, target = float(gate_args[0]), symqbit[int(gate_args[1])]
        return Rz(target,theta)

    if gate_name == "crz":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            theta = float(args1)
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            theta = float(args1[0])
            target = symqbit[int(args1[2])]
            control = symqbit[int(args1[1])]
        return Rz(target,theta).controlled_by(control)

    if gate_name == "swap":
        gate_args = gate_args.split(",")
        target1, target2 = symqbit[int(gate_args[0])], symqbit[int(gate_args[1])]
        return SWAP(target1,target2)

    if gate_name == "iswap":
        gate_args = gate_args.split(",")
        target1, target2 = symqbit[int(gate_args[0])], symqbit[int(gate_args[1])]
        return ISWAP(target1,target2)

    if gate_name == "cswap":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            target1, target2 = symqbit[int(args3[0])], symqbit[int(args3[1])]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            target1 = symqbit[int(args1[1])]
            target2 = symqbit[int(args1[2])]
            control = symqbit[int(args1[0])]
        return SWAP(target1,target2).controlled_by(control)

    if gate_name == "sx":
        target = symqbit[int(gate_args[0])]
        return V(target)

    if gate_name == "sxdg":
        target = symqbit[int(gate_args[0])]
        return V_dag(target)

    if gate_name == "csx":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            target = symqbit[int(args1[1])]
            control = symqbit[int(args1[0])]
        return V(target).controlled_by(control)

    if gate_name == "u":
        gate_args = gate_args.split(",")
        theta, phi, lam, target = float(gate_args[0]), float(gate_args[1]), float(gate_args[2]), symqbit[int(gate_args[3])]
        return U3(target,theta,phi,lam)

    if gate_name == "cu":
        flag, args1, args2, args3 = args_split(gate_args)
        if flag:
            phase_list = gate_args.split("[")[0][:-1].split(",")
            theta, phi, lam = float(phase_list[0]), float(phase_list[1]), float(phase_list[2])
            target = symqbit[int(args3)]
            control = ""
            for i in args2:
                control.append(symqbit[int(i)])
        else:
            theta, phi, lam = float(args1[0]), float(args1[1]), float(args1[2])
            target = symqbit[int(args1[5])]
            control = symqbit[int(args1[4])]
        return U3(target,theta,phi,lam).controlled_by(control)



def operations_to_program(num_qbits, operations):
    program = []
    for operation in operations:
        program.append(operation_to_method(num_qbits,operation))
    return program


if __name__ == "__main__":
    num_qbits=3
    operations =[
                 "cx(0,1)",
                 ]
    print(operations_to_program(3, operations))