

def fun(x, qc):
    x+=1
    print(qc.getConcrValue())
    qc.h(0)
    print(qc.getConcrValue())
    if x > 10:
        qc.h(1)
    else:
        qc.z(0)
    print(qc.getConcrValue())