
class ModuleRegistry:
    def __init__(self):
        self.modules = []

    def register(self, module):
        self.modules.append(module)

    

    def dispatch(self, query: str):
        for module in self.modules:
            print("Checking:", module.__class__.__name__)
            if module.supports(query):
                print("Matched:", module.__class__.__name__)
                return module.solve(query)

        print("No module matched")
        return None
