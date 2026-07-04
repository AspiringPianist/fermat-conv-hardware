MODULUS = 65537
BIT_WIDTH = 16
MASK = (1 << BIT_WIDTH) - 1


class ModularArithmetic:
    @staticmethod
    def reduce(x: int) -> int:
        """
        Fast reduction modulo 65537 = 2^16 + 1.

        Uses:
            x = x_low + 2^16 * x_high
            x mod 65537 = x_low - x_high
        """

        while x < 0 or x > MASK:
            low = x & MASK
            high = x >> BIT_WIDTH
            x = low - high

        if x < 0:
            x += MODULUS
        elif x == MODULUS:
            x = 0

        return x

    @staticmethod
    def add(a: int, b: int) -> int:
        return ModularArithmetic.reduce(a + b)

    @staticmethod
    def subtract(a: int, b: int) -> int:
        return ModularArithmetic.reduce(a - b)

    @staticmethod
    def multiply(a: int, b: int) -> int:
        return ModularArithmetic.reduce(a * b)

    @staticmethod
    def power(base: int, exponent: int) -> int:
        return pow(base, exponent, MODULUS)

    @staticmethod
    def inverse(a: int) -> int:
        return pow(a, MODULUS - 2, MODULUS)
