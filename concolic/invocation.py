class FunctionInvocation:
    # 可执行的函数类
    def __init__(self, function, reset):
        self.function = function
        self.reset = reset
        # 参数的构建器， 对于不同的参数类型，拥有不同的构建参数的办法
        self.arg_constructor = {}
        # 参数的初始值设定
        self.initial_value = {}

    def callFunction(self, args):
        # 执行当前的函数，先重置函数，然后将参数的字典传给函数，进行执行
        self.reset()
        return self.function(**args)

    def addArgumentConstructor(self, name, init, constructor):
        # 为参数设置初始值和构建器
        self.initial_value[name] = init
        self.arg_constructor[name] = constructor

    def getNames(self):
        # 返回当前函数的所有可变参数
        return self.arg_constructor.keys()

    def createArgumentValue(self, name, val=None):
        # 对目标的参数，将初始值和名字传输给相应类型的构建器中
        # 生成一个目标类型的变量参数
        if val == None:
            val = self.initial_value[name]
        return self.arg_constructor[name](name, val)