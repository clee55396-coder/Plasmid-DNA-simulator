
import streamlit as st
from dna_analysis import analyze_plasmid, get_pattern
st.set_page_config(
    page_title="플라스미드 DNA 시뮬레이터",
    page_icon="🧬",
    layout="wide"
)
def make_gel_html(fragments):
    import math

    bands = ""

    for size in sorted(set(fragments), reverse=True):
        position = 25 + 140 * (4 - math.log10(size))
        position = max(20, min(320, position))

        bands += (
            f'<div style="position:absolute;top:{position:.0f}px;'
            'left:45px;width:170px;height:6px;'
            'background:#8efbff;'
            'box-shadow:0 0 10px #8efbff;"></div>'
            f'<span style="position:absolute;top:{position-7:.0f}px;'
            'left:225px;color:white;font-size:13px;">'
            f'{size} bp</span>'
        )

    return (
        '<div style="height:360px;width:330px;'
        'position:relative;background:#07132b;'
        'border:1px solid #445;border-radius:8px;">'
        + bands +
        '</div>'
    )


st.title("🧬 플라스미드 DNA 시뮬레이터")

st.write(
    "DNA 염기서열과 제한효소를 선택하여 "
    "원형 플라스미드의 절단 패턴을 분석합니다."
)

st.divider()

# 예시 플라스미드 DNA
example_dna = (
    "A" * 100 + "GAATTC"
    + "A" * 794 + "GAATTC"
    + "A" * 1194 + "GAATTC"
    + "A" * 894
)

st.subheader("1. DNA 염기서열 입력")

dna = st.text_area(
    "원형 플라스미드 DNA",
    value=example_dna,
    height=150
)

st.subheader("2. 제한효소 선택")

enzymes = {
    "EcoRI": "GAATTC",
    "BamHI": "GGATCC",
    "HindIII": "AAGCTT"
}

selected = st.selectbox(
    "사용할 제한효소",
    list(enzymes.keys())
)

st.divider()

if st.button("🔬 DNA 분석하기", type="primary"):

    result = analyze_plasmid(
        dna,
        enzymes[selected]
    )

    if "error" in result:
        st.error(result["error"])

    else:
        st.success("DNA 분석 완료!")

        st.metric(
            "DNA 길이",
            f"{result['dna_length']} bp"
        )

        st.write(
            "**제한효소:**",
            selected
        )

        st.write(
            "**절단 조각 크기:**",
            result["fragments"]
        )

        st.write(
            "**절단 지점 수:**",
            result["cut_count"]
        )
        
        # 3. 전기영동 밴드 시뮬레이션
        st.subheader("3. 전기영동 밴드 예측")

        if result["fragments"]:

            import math

            bands = ""

            for size in sorted(set(result["fragments"]), reverse=True):

                # DNA 크기를 이용한 이동 위치 계산
                position = 25 + 140 * (4 - math.log10(size))
                position = max(20, min(320, position))

                bands += (
                    f'<div style="position:absolute;top:{position:.0f}px;'
                    'left:45px;width:170px;height:6px;'
                    'background:#8efbff;'
                    'box-shadow:0 0 10px #8efbff;"></div>'
                    f'<span style="position:absolute;top:{position-7:.0f}px;'
                    'left:225px;color:white;font-size:13px;">'
                    f'{size} bp</span>'
                )

            gel = (
                '<div style="height:360px;width:330px;'
                'position:relative;background:#07132b;'
                'border:1px solid #445;border-radius:8px;">'
                + bands + '</div>'
            )

            st.markdown(gel, unsafe_allow_html=True)

            st.caption(
                "DNA 크기를 바탕으로 밴드 위치를 단순 예측한 "
                "시뮬레이션입니다. 실제 실험 결과와는 차이가 있습니다."
            )

        else:
            st.info(
                "절단 지점이 없어 선형 DNA 조각의 "
                "밴드 위치를 예측하지 않습니다."
            )








        st.divider()
        st.subheader("4. 원본 vs 변이 DNA 비교")

        current_dna = "".join(dna.upper().split())

        mut_pos = st.number_input(
            "변이 위치",
            min_value=1,
            max_value=len(current_dna),
            value=1,
            step=1
        )

        original_base = current_dna[mut_pos - 1]

        available_bases = [b for b in "ACGT" if b != original_base]

        new_base = st.selectbox(
            f"{mut_pos}번째 염기의 현재 값: {original_base} → 변경할 염기",
            available_bases
        )

        if st.button("🧪 원본 vs 변이 비교하기"):

            mutant_dna = (
                current_dna[:mut_pos - 1]
                + new_base
                + current_dna[mut_pos:]
            )

            original_fragments = get_pattern(
                current_dna, enzymes[selected]
            )

            mutant_fragments = get_pattern(
                mutant_dna, enzymes[selected]
            )

            st.write(
                f"**변이 내용:** {mut_pos}번째 염기 "
                f"{original_base} → {new_base}"
            )

            if original_fragments == mutant_fragments:
                st.info("절단 패턴이 동일하여 이 효소로 구별할 수 없습니다.")
            else:
                st.success("절단 패턴이 달라져 이 효소로 구별할 수 있습니다.")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**원본 DNA**")
                st.write(original_fragments)
                st.markdown(
                    make_gel_html(original_fragments),
                    unsafe_allow_html=True
                )

            with col2:
                st.write("**변이 DNA**")
                st.write(mutant_fragments)
                st.markdown(
                    make_gel_html(mutant_fragments),
                    unsafe_allow_html=True
                )
