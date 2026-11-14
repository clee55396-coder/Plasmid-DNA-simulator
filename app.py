
import streamlit as st
from dna_analysis import analyze_plasmid

st.set_page_config(
    page_title="플라스미드 DNA 시뮬레이터",
    page_icon="🧬",
    layout="wide"
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

