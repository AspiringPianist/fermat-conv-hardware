from software.modular_arithmetic import ModularArithmetic


class PolynomialMultiplier:
    def __init__(self, ntt):
        self.ntt = ntt

    def pointwise_multiply(self, A, B):

        coeffs = A.coefficients.copy()

        for i in range(len(coeffs)):
            coeffs[i] = ModularArithmetic.multiply(
                A.coefficients[i],
                B.coefficients[i],
            )

        return A.__class__(
            coefficients=coeffs,
            rand=False,
            degree=A.degree,
        )

    def multiply(self, poly_a, poly_b):

        #
        # Negacyclic preprocessing
        #
        A = self.ntt.preprocess(poly_a)
        B = self.ntt.preprocess(poly_b)

        #
        # Forward transforms
        #
        A = self.ntt.forward(A)
        B = self.ntt.forward(B)

        #
        # Pointwise multiplication
        #
        C = self.pointwise_multiply(A, B)

        #
        # Inverse transform
        #
        C = self.ntt.inverse(C)

        #
        # Undo preprocessing
        #
        C = self.ntt.postprocess(C)

        return C
