from software.butterfly import R2Butterfly


class Stage:
    """
    Represents one stage of the radix-2 NTT.

    A Stage does not own the twiddle factors.
    It simply requests them from TwiddleMemory.
    """

    def __init__(self, stage_index: int, N: int):
        self.stage_index = stage_index
        self.N = N

    def execute(self, coefficients, twiddle_memory):
        """
        Execute one radix-2 NTT stage.

        Parameters
        ----------
        coefficients : list[int]
            Current polynomial coefficients.

        twiddle_memory : TwiddleMemory
            Object responsible for supplying stage twiddle factors.

        Returns
        -------
        list[int]
            Updated coefficient array.
        """

        output = coefficients.copy()

        butterfly_distance = 1 << self.stage_index
        butterfly_span = butterfly_distance << 1

        twiddle_index = 0

        for block_start in range(0, self.N, butterfly_span):
            for offset in range(butterfly_distance):
                a_index = block_start + offset
                b_index = a_index + butterfly_distance

                w = twiddle_memory.get(
                    self.stage_index,
                    offset,
                )

                output[a_index], output[b_index] = R2Butterfly.compute(
                    output[a_index],
                    output[b_index],
                    w,
                )

                twiddle_index += 1

        return output
