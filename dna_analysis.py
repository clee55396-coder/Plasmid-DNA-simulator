
# 원형 DNA의 제한효소 절단 분석
def get_pattern(dna, enzyme):
    dna = dna.upper()
    enzyme = enzyme.upper()

    length = len(dna)
    circular = dna + dna[:len(enzyme)-1]

    cuts = []

    for i in range(length):
        if circular[i:i+len(enzyme)] == enzyme:
            cuts.append((i+1) % length)

    cuts.sort()

    if len(cuts) == 0:
        return ()

    if len(cuts) == 1:
        return (length,)

    fragments = []

    for i in range(len(cuts)):
        start = cuts[i]
        end = cuts[(i+1) % len(cuts)]
        fragments.append((end-start) % length)

    return tuple(sorted(fragments))


# DNA 분석 함수
def analyze_plasmid(dna, enzyme):
    dna = "".join(dna.upper().split())

    if not dna:
        return {"error": "DNA를 입력해 주세요."}

    if any(base not in "ACGT" for base in dna):
        return {"error": "DNA는 A, C, G, T만 입력할 수 있습니다."}

    if len(dna) < len(enzyme):
        return {"error": "DNA 길이가 너무 짧습니다."}

    fragments = get_pattern(dna, enzyme)

    return {
        "dna_length": len(dna),
        "enzyme": enzyme,
        "fragments": fragments,
        "cut_count": len(fragments) if fragments else 0
    }
