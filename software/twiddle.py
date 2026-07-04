# the primitive generator for F4 = 65537 = 2^16+1 is 3
# This means 3^0, 3^1, ...., 3^65535 span the multiplicative group of F4 which is [1, 65536]
# Imagine these forming a circle. the 65536 root of unity is 3^1 and then the 8192 root of unity is 65536/8192 = 8 so 3^8
#
# Here comes the power of 2 optimization. Since 2^16 = -1 (modd 65537), 2^32 = 1 which means 2 itself is a primitive 32nd root of unity.
#
from software.modular_arithmetic import ModularArithmetic

MODULUS = 65537
PRIMITIVE_GENERATOR = 3


class TwiddleGenerator:
    def __init__(self, N):
        self.N = N

        self.omega_N = self._primitive_root(N)
        self.omega_2N = self._primitive_root(2 * N)

        self.forward = self._generate_table(self.omega_N)
        self.inverse = self._generate_table(
            ModularArithmetic.power(self.omega_N, MODULUS - 2)
        )

        self.preprocess = self._generate_table(self.omega_2N)
        self.postprocess = self._generate_table(
            ModularArithmetic.power(self.omega_2N, MODULUS - 2)
        )

    def _primitive_root(self, order):
        if (MODULUS - 1) % order != 0:
            raise ValueError("Order must divide q-1")

        exponent = (MODULUS - 1) // order
        return ModularArithmetic.power(PRIMITIVE_GENERATOR, exponent)

    def _generate_table(self, omega):
        table = []

        value = 1
        for _ in range(self.N):
            table.append(value)
            value = ModularArithmetic.multiply(value, omega)

        return table

    def is_power_of_two(self, value):
        current = 1

        for shift in range(32):
            if current == value:
                return True, shift

            current = (current * 2) % MODULUS

        return False, None
