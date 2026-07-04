from math import log2

from software.modular_arithmetic import ModularArithmetic
from software.polynomial import Polynomial
from software.stage import Stage


def _bit_reverse(coefficients, N):
    bits = int(log2(N))
    output = [0] * N
    for i in range(N):
        reversed_index = int(format(i, f"0{bits}b")[::-1], 2)
        output[reversed_index] = int(coefficients[i])
    return output


class NTT:
    """
    Executes both the Forward and Inverse Number Theoretic Transform.
    """

    def __init__(self, N, twiddle_generator):
        self.N = N
        self.num_stages = int(log2(N))

        self.forward_memory = twiddle_generator.forward_memory
        self.inverse_memory = twiddle_generator.inverse_memory

        self.preprocess_twiddles = twiddle_generator.preprocess
        self.postprocess_twiddles = twiddle_generator.postprocess

    def preprocess(self, polynomial: Polynomial):
        coeffs = polynomial.coefficients.flatten().copy()
        for i in range(self.N):
            coeffs[i] = ModularArithmetic.multiply(
                coeffs[i],
                self.preprocess_twiddles[i],
            )

        return Polynomial(
            coefficients=coeffs,
            rand=False,
            degree=self.N - 1,
        )

    def postprocess(self, polynomial: Polynomial):
        coeffs = polynomial.coefficients.flatten().copy()
        for i in range(self.N):
            coeffs[i] = ModularArithmetic.multiply(
                coeffs[i],
                self.postprocess_twiddles[i],
            )

        return Polynomial(
            coefficients=coeffs,
            rand=False,
            degree=self.N - 1,
        )

    def forward(self, polynomial: Polynomial):

        coeffs = _bit_reverse(polynomial.coefficients, self.N)

        for stage_idx in range(self.num_stages):
            stage = Stage(stage_idx, self.N)

            coeffs = stage.execute(
                coeffs,
                self.forward_memory,
            )

        coeffs = _bit_reverse(coeffs, self.N)

        return Polynomial(
            coefficients=coeffs,
            rand=False,
            degree=self.N - 1,
        )

    def inverse(self, polynomial: Polynomial):

        coeffs = polynomial.coefficients.copy()

        for stage_idx in range(self.num_stages):
            stage = Stage(stage_idx, self.N)

            coeffs = stage.execute(
                coeffs,
                self.inverse_memory,
            )

        inv_N = ModularArithmetic.inverse(self.N)

        for i in range(self.N):
            coeffs[i] = ModularArithmetic.multiply(
                coeffs[i],
                inv_N,
            )

        return Polynomial(
            coefficients=coeffs,
            rand=False,
            degree=self.N - 1,
        )
