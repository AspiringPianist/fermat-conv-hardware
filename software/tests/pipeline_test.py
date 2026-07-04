from software.modular_arithmetic import ModularArithmetic
from software.ntt import NTT
from software.polynomial import Polynomial
from software.polynomial_multiplier import PolynomialMultiplier
from software.twiddle import TwiddleGenerator


class NaivePolynomialMultiplier:
    """
    Schoolbook O(N²) polynomial multiplication.

    Golden reference for verifying the full NTT pipeline.
    """

    @staticmethod
    def multiply_raw(A: Polynomial, B: Polynomial):
        """
        Compute full convolution (degree 2N - 2).
        """

        a = A.coefficients.flatten()
        b = B.coefficients.flatten()

        N = len(a)

        result = [0] * (2 * N - 1)

        for i in range(N):
            for j in range(N):
                product = ModularArithmetic.multiply(a[i], b[j])

                result[i + j] = ModularArithmetic.add(
                    result[i + j],
                    product,
                )

        return result

    @staticmethod
    def reduce_negacyclic(coefficients, N):
        """
        Reduce modulo x^N + 1 using:
            x^N = -1
        """

        reduced = [0] * N

        # lower part
        for i in range(N):
            reduced[i] = coefficients[i]

        # fold upper part
        for i in range(N, len(coefficients)):
            reduced[i - N] = ModularArithmetic.subtract(
                reduced[i - N],
                coefficients[i],
            )

        return reduced

    def multiply(self, A: Polynomial, B: Polynomial):
        """
        Full reference multiplication:
        raw convolution + negacyclic reduction
        """

        raw = self.multiply_raw(A, B)

        reduced = self.reduce_negacyclic(
            raw,
            len(A.coefficients),
        )

        return Polynomial(
            coefficients=reduced,
            rand=False,
            degree=len(reduced) - 1,
        )


def compare_pipeline_vs_naive(pipeline, A: Polynomial, B: Polynomial):
    """
    Compare full NTT pipeline against naive multiplier.
    """
    print("comparing pipeline vs naive implementation")
    print("starting naive")
    golden = NaivePolynomialMultiplier()

    expected = golden.multiply(A, B)
    print("done with naive, starting pipeline")
    actual = pipeline.multiply(A, B)
    print("done with pipeline, comparing results")

    expected = expected.coefficients.flatten()
    actual = actual.coefficients.flatten()

    if len(expected) != len(actual):
        print("Length mismatch")
        print("Expected:", len(expected))
        print("Actual  :", len(actual))
        return False

    success = True

    for i in range(len(expected)):
        if int(expected[i]) != int(actual[i]):
            print(f"Mismatch at index {i}")
            print("Expected:", expected[i])
            print("Actual  :", actual[i])
            success = False

    if success:
        print("✔ PASS: Pipeline matches naive multiplication")
    else:
        print("✖ FAIL: Mismatch detected")

    return success


if __name__ == "__main__":
    N = 8

    poly_a = Polynomial(
        coefficients=None,
        rand=True,
        degree=N - 1,
    )

    poly_b = Polynomial(
        coefficients=None,
        rand=True,
        degree=N - 1,
    )

    print("Polynomial A:")
    print(poly_a)
    print()

    print("Polynomial B:")
    print(poly_b)
    print()

    #
    # Hook your pipeline here:
    #
    print("generating twidddles")
    twiddle = TwiddleGenerator(N)
    print("done generating twiddles")
    ntt = NTT(N, twiddle)
    pipeline = PolynomialMultiplier(ntt)

    compare_pipeline_vs_naive(pipeline, poly_a, poly_b)
