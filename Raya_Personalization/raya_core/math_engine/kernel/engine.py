 # kernel/engine.py
from .registry import ModuleRegistry


class ComputationKernel:

    def __init__(self):
        self.registry = ModuleRegistry()

    def register_module(self, module):
        self.registry.register(module)

    def compute(self, query: str):
        return self.registry.dispatch(query)
