import numpy as np

MODULUS = 65537


class Polynomial:
    def __init__(self, coefficients, rand, degree):
        if not rand:
            # we assume that the input coefficients are already within the fermat modulus ring.
            self.coefficients = coefficients.copy()
            self.degree = len(coefficients) - 1
        if rand:
            # create a degree + 1 size array with 1 columns and (degree + 1) rows
            self.coefficients = np.random.randint(0, 65537, size=(degree + 1, 1))
            self.degree = degree

    def update_coefficient(self, index, value):
        self.coefficients[index] = value

    def __str__(self):
        terms = []

        for power, coeff in enumerate(self.coefficients.flatten()):
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
