class SemanticChecker:
    def __init__():
        self.symbol_table = {}

    def check(self, ast):
        for node in ast:
            method = getattr(self, f"_check_{node}", self._check_generic)
            return method()

    def _check_generic(self, node):
        pass

    def _check_declare(self, node):
        pass
