from software.modular_arithmetic import ModularArithmetic


class R2Butterfly:
    @staticmethod
    def compute(a: int, b: int, w: int):
        if isinstance(w, dict) and w["is_pow2"]:
            # SHIFT NETWORK (NO MULTIPLICATION)
            second_term = ModularArithmetic.multiply(b, (1 << w["shift"]))
        else:
            second_term = ModularArithmetic.multiply(b, w["value"])
        return (
            ModularArithmetic.add(a, second_term),
            ModularArithmetic.subtract(a, second_term),
        )
