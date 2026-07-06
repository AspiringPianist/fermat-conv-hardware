"""Analyze shift vs full twiddle multiplications across N."""

from math import log2

from software.twiddle import TwiddleGenerator


def classify_ntt_memory(gen, memory):
    shift = full = trivial = 0
    for stage_idx in range(memory.num_stages()):
        step = 1 << stage_idx
        uses_per_offset = gen.N // (2 * step)
        for w in memory.stage(stage_idx):
            if w["is_pow2"]:
                if w["value"] == 1:
                    trivial += uses_per_offset
                else:
                    shift += uses_per_offset
            else:
                full += uses_per_offset
    total = shift + full + trivial
    return {"shift": shift, "full": full, "trivial": trivial, "total": total}


def classify_table(gen, table):
    shift = full = trivial = 0
    for val in table:
        is_pow2, _ = gen.is_power_of_two(val)
        if is_pow2:
            if val == 1:
                trivial += 1
            else:
                shift += 1
        else:
            full += 1
    return {"shift": shift, "full": full, "trivial": trivial, "total": len(table)}


def analyze(N):
    gen = TwiddleGenerator(N)
    fwd = classify_ntt_memory(gen, gen.forward_memory)
    inv = classify_ntt_memory(gen, gen.inverse_memory)
    pre = classify_table(gen, gen.preprocess)
    post = classify_table(gen, gen.postprocess)

    # Full polynomial multiply: 2x pre, 2x fwd, 1x inv, 1x post
    pipe_shift = 2 * pre["shift"] + 2 * fwd["shift"] + inv["shift"] + post["shift"]
    pipe_full = 2 * pre["full"] + 2 * fwd["full"] + inv["full"] + post["full"]
    pipe_trivial = (
        2 * pre["trivial"]
        + 2 * fwd["trivial"]
        + inv["trivial"]
        + post["trivial"]
    )
    pipe_total = pipe_shift + pipe_full + pipe_trivial

    pointwise = N
    inv_scale = N
    all_total = pipe_total + pointwise + inv_scale
    all_full = pipe_full + pointwise + inv_scale

    return {
        "N": N,
        "stages": int(log2(N)),
        "butterflies_per_ntt": (N // 2) * int(log2(N)),
        "forward": fwd,
        "inverse": inv,
        "preprocess": pre,
        "postprocess": post,
        "pipe_shift": pipe_shift,
        "pipe_full": pipe_full,
        "pipe_trivial": pipe_trivial,
        "pipe_total": pipe_total,
        "pointwise": pointwise,
        "inv_scale": inv_scale,
        "all_total": all_total,
        "all_full": all_full,
    }


def pct(n, d):
    return 100.0 * n / d if d else 0.0


if __name__ == "__main__":
    sizes = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]

    print("Twiddle multiply classification (q=65537, radix-2 DIT NTT)")
    print()
    header = (
        f"{'N':>6} | {'bflies':>6} | "
        f"{'fwd sh':>6} {'fwd fm':>6} | "
        f"{'inv sh':>6} {'inv fm':>6} | "
        f"{'pipe sh%':>7} {'pipe fm%':>7} {'pipe tr%':>7} | "
        f"{'all sh%':>7} {'all fm%':>7}"
    )
    print(header)
    print("-" * len(header))

    for N in sizes:
        if 65536 % N != 0:
            continue
        s = analyze(N)
        print(
            f"{s['N']:6d} | {s['butterflies_per_ntt']:6d} | "
            f"{s['forward']['shift']:6d} {s['forward']['full']:6d} | "
            f"{s['inverse']['shift']:6d} {s['inverse']['full']:6d} | "
            f"{pct(s['pipe_shift'], s['pipe_total']):7.1f} "
            f"{pct(s['pipe_full'], s['pipe_total']):7.1f} "
            f"{pct(s['pipe_trivial'], s['pipe_total']):7.1f} | "
            f"{pct(s['pipe_shift'], s['all_total']):7.1f} "
            f"{pct(s['all_full'], s['all_total']):7.1f}"
        )

    print()
    print("Legend: sh=shift (pow2 twiddle), fm=full multiply (non-pow2 twiddle),")
    print("        tr=trivial (w=1), pipe=full negacyclic mult pipeline twiddles only,")
    print("        all=pipe + N pointwise + N inverse-scale multiplies")

    print()
    print("Butterfly twiddles only (one forward NTT):")
    print(f"{'N':>6}  {'bflies':>7}  {'shift':>7}  {'full':>7}  {'shift%':>6}  {'full%':>6}")
    for N in sizes:
        if 65536 % N != 0:
            continue
        f = analyze(N)["forward"]
        print(
            f"{N:6d}  {f['total']:7d}  {f['shift']:7d}  {f['full']:7d}  "
            f"{pct(f['shift'], f['total']):6.1f}  {pct(f['full'], f['total']):6.1f}"
        )

    print()
    print("Pre/post twiddles (one pass, N coefficients):")
    print(f"{'N':>6}  {'shift':>7}  {'full':>7}  {'full%':>6}")
    for N in [8, 256, 1024, 8192, 32768]:
        p = analyze(N)["preprocess"]
        print(
            f"{N:6d}  {p['shift']:7d}  {p['full']:7d}  {pct(p['full'], p['total']):6.1f}"
        )
