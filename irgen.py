class IRGenerator:
    def __init__(self):
        self.module = None
        # self.module.tripple 
        self.function = None
        self.scope = None
        

    def generate(self, ast):
        self._(ast)
        return str(self.module)

    def _(self, node):
        return getattr(self, f"_{node[0]}","__generic")(node)

    def __generic(self, node):
        for child in node if isinstance(node, list) else node[1]:
            if isinstance(child, tuple):
                self._(child)

    def _declare(self, node):
        pass

    def _assign(self, node):
        pass

    def _declare_assign(self, node):
        pass
    
    def _lambda_func(self, node):
        pass

    def _enum_declare(self, node):
        pass
    
    def _array_lit(self, node):
        pass
    
    def _index(self, node):
        pass

    def _spread(self, node):
        pass

    def _modifier(sel, nodef)
        pass

    def _pass(self, node):
        pass

    def _return(self, node):
        pass

    def _func_declare(self, node):
        pass

    def _struct(self, node):
        pass

    def _struct_ctor(self, node):
        pass

    def _when_stmt(self, node):
        pass

    def _when(self, node):
        pass

    def _when_default(self, node):
        pass

    def _loop(self, node):
        pass

    def _until(self, node):
        pass

    def _func_call(self, node):
        pass

    def _binop(self, node):
        pass

    def _unary(self, node):
        pass

    def _logic_not(self, node):
        pass

    def _logic_and(self, node):
        pass

    def _logic_or(self, node):
        pass

    def _conop(self, node):
        pass

    def _access(self, node):
        pass

    def _string(self, node):
        pass

    def _boolean(self, node):
        pass

    def _id(self, node):
        pass

    def _cast(self, node):
        pass

    def _range(self, node):
        pass

    def _array(self, node):
        pass

    def _dict_lit(self, node):
        pass