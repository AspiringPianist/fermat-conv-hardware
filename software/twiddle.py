# the primitive generator for F4 = 65537 = 2^16+1 is 3
# This means 3^0, 3^1, ...., 3^65535 span the multiplicative group of F4 which is [1, 65536]
# Imagine these forming a circle. the 65536 root of unity is 3^1 and then the 8192 root of unity is 65536/8192 = 8 so 3^8
#
# Here comes the power of 2 optimization. Since 2^16 = -1 (modd 65537), 2^32 = 1 which means 2 itself is a primitive 32nd root of unity.
#
from math import log2

from software.modular_arithmetic import ModularArithmetic

MODULUS = 65537
PRIMITIVE_GENERATOR = 3


class TwiddleMemory:
    """
    Stores stage-wise twiddle factors.

    Example (N = 8)

    Stage 0 : [1]

    Stage 1 : [1, ω²]

    Stage 2 : [1, ω, ω², ω³]
    """

    def __init__(self, stage_tables):
        self.stage_tables = stage_tables

    def get(self, stage: int, offset: int) -> int:
        """
        Returns the twiddle factor required by a butterfly
        at a given stage and butterfly offset.
        """
        return self.stage_tables[stage][offset]

    def stage(self, stage: int):
        """
        Returns all twiddle factors for a stage.
        """
        return self.stage_tables[stage]

    def num_stages(self):
        return len(self.stage_tables)

    def __len__(self):
        return len(self.stage_tables)

    def __getitem__(self, stage):
        return self.stage_tables[stage]

    def __str__(self):
        output = []

        for stage, twiddles in enumerate(self.stage_tables):
            output.append(f"Stage {stage}: {twiddles}")

        return "\n".join(output)


class TwiddleGenerator:
    def __init__(self, N):
        self.N = N

        self.omega_N = self._primitive_root(N)
        self.omega_2N = self._primitive_root(2 * N)

        self.forward = self._generate_table(self.omega_N)
        self.inverse = self._generate_table(ModularArithmetic.inverse(self.omega_N))

        self.preprocess = self._generate_table(self.omega_2N)
        self.postprocess = self._generate_table(
            ModularArithmetic.inverse(self.omega_2N)
        )

        self.forward_memory = TwiddleMemory(self._generate_stage_tables(self.forward))

        self.inverse_memory = TwiddleMemory(self._generate_stage_tables(self.inverse))

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

    def _generate_stage_tables(self, table):
        """
        Generate stage-wise twiddle tables.

        Stage 0 : 1
        Stage 1 : 1, ω^(N/4)
        Stage 2 : 1, ω^(N/8), ω^(2N/8), ...
        """

        stages = []

        num_stages = int(log2(self.N))

        for stage in range(num_stages):
            step = 1 << stage
            stride = self.N // (2 * step)

            stage_table = []

            for butterfly in range(step):
                exponent = butterfly * stride
                val = table[exponent]
                is_pow2, shift = self.is_power_of_two(val)
                stage_table.append({"value": val, "is_pow2": is_pow2, "shift": shift})

            stages.append(stage_table)

        return stages

    def is_power_of_two(self, value):
        current = 1

        for shift in range(32):
            if current == value:
                return True, shift

            current = ModularArithmetic.multiply(current, 2)

        return False, None
