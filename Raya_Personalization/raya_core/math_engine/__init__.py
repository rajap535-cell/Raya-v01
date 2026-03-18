#math engine/_init_.py

from .kernel.engine import ComputationKernel

from .modules.symbolic import SymbolicMathModule
from .modules.arithmetic import ArithmeticModule
from .modules.percentage import PercentageModule
from .modules.algebra import AlgebraModule


_kernel = ComputationKernel()

_kernel.register_module(PercentageModule())
_kernel.register_module(SymbolicMathModule())
_kernel.register_module(ArithmeticModule())
_kernel.register_module(AlgebraModule())


def solve_math(query: str):
    result = _kernel.compute(query)

    if not result:
        return None

    # unwrap module output
    if isinstance(result, dict) and "result" in result:
        value = result["result"]

        # clean integer floats
        if isinstance(value, float) and value.is_integer():
            value = int(value)

        return str(value)

    return str(result)
