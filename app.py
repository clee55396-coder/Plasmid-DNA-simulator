
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
