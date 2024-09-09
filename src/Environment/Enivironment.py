class Environment:
    def __init__(self, Parent=None, Num=0):
        self.Parent = Parent
        self.Variables = {}
        self.Functions = {}
        self.NameSpace = {}

        self.ScopeNum = Num

        self.DecError = "Var Exist"
        self.UnKownVar = "Var Does Not Exist"

    def declarevar(self, VarName, Value):
        if VarName in list(self.Variables.keys()):
            print("Vraible Exist Blud")
            return self.DecError

        Value.update({"VarScopeName":f"{VarName}_{self.ScopeNum}"})
        self.Variables.update({VarName : Value})
        return VarName

    def AssingVar(self, VarName, Value):
        Env = self.Resolve(VarName)
        if Env == {}:
            return self.UnKownVar

        Env[VarName]["Value"] = Value
        return 
    
    
    def LookupVar(self, VarName):
        Env = self.Resolve(VarName)
        if Env == {}:
            return self.UnKownVar
        return Env.get(VarName)

    def Resolve(self, VarName):
        if VarName in list(self.Variables.keys()):
            return self.Variables

        if self.Parent == None:
            return {}        

        return self.Parent.Resolve(VarName)

    def declarefunc(self, VarName, Value):
        if VarName in list(self.Functions.keys()):
            print("Vraible Exist Blud")
            return self.DecError

        # if "VarScopeName" not in list(Value.keys()):
        #     Value.update({"VarScopeName":f"{VarName}_{self.ScopeNum}"})
        self.Functions.update({VarName : Value})
        return Value

    def Assingfunc(self, VarName, Value):
        Env = self.Resolvefunc(VarName)
        if Env == {}:
            return self.UnKownVar

        Env[VarName]["Body"] = Value
        return 
    
    
    def Lookupfunc(self, VarName):
        Env = self.Resolvefunc(VarName)
        if Env == {}:
            return self.UnKownVar
        return Env.get(VarName)

    def Resolvefunc(self, VarName):
        if VarName in list(self.Functions.keys()):
            return self.Functions

        if self.Parent == None:
            return {}        

        return self.Parent.Resolvefunc(VarName)


    def declareNamesp(self, VarName, Value, env):
        import copy

        ValueCopy = copy.deepcopy(Value)

        if "VarScopeName" not in list(Value.keys()):
            Value.update({"VarScopeName":f"{VarName}_{self.ScopeNum}"})
            ValueCopy.update({"VarScopeName":f"{VarName}_{self.ScopeNum}"})

        if "Environment" not in list(Value.keys()):
            ValueCopy.update({"Environment":env})

        if VarName in list(self.NameSpace.keys()):
           self.NameSpace[VarName]["Property"] = self.NameSpace[VarName]["Property"] + Value["Property"]
        else:
            self.NameSpace.update({VarName : ValueCopy})
        
        return Value
    
    def LookupNamesp(self, VarName):
        Env = self.ResolveNamesp(VarName)
        if Env == {}:
            return self.UnKownVar
        return Env.get(VarName)

    def ResolveNamesp(self, VarName):
        if VarName in list(self.NameSpace.keys()):
            return self.NameSpace

        if self.Parent == None:
            return {}        

        return self.Parent.ResolveNamesp(VarName)