import numpy as np

MODULUS = 65537


class Polynomial:
    def __init__(self, coefficients, rand, degree):
        if not rand:
            # we assume that the input coefficients are already within the fermat modulus ring.
            self.coefficients = np.asarray(coefficients, dtype=np.int64).ravel()
            self.degree = len(self.coefficients) - 1
        if rand:
            self.coefficients = np.random.randint(0, 65537, size=degree + 1, dtype=np.int64)
            self.degree = degree

    def update_coefficient(self, index, value):
        self.coefficients[index] = value

    def __str__(self):
        terms = []

        for power, coeff in enumerate(self.coefficients):
            if coeff == 0:
                continue

            if power == 0:
                terms.append(f"{coeff}")
            elif power == 1:
                terms.append(f"{coeff}x")
            else:
                terms.append(f"{coeff}x^{power}")

        if not terms:
            return "0"

        return " + ".join(terms)
