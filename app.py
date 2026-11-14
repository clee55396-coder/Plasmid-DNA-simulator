
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
    st.session_state["show_analysis"] = True

if st.session_state.get("show_analysis", False):

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

        st.divider()
        st.subheader("5. 단일 염기 치환 자동 분석")

        st.write(
            "DNA의 모든 위치에서 가능한 단일 염기 치환을 "
            "분석하여 절단 패턴이 변하는 경우를 계산합니다."
        )

        if st.button("🧬 전체 변이 분석하기"):

            original_dna = "".join(dna.upper().split())
            enzyme = enzymes[selected]

            original_pattern = get_pattern(
                original_dna, enzyme
            )

            detected = 0
            total = 0

            with st.spinner("변이를 분석하는 중입니다..."):

                for i in range(len(original_dna)):
                    for base in "ACGT":

                        if base == original_dna[i]:
                            continue

                        mutant = (
                            original_dna[:i]
                            + base
                            + original_dna[i+1:]
                        )

                        mutant_pattern = get_pattern(
                            mutant, enzyme
                        )

                        total += 1

                        if mutant_pattern != original_pattern:
                            detected += 1

            undetected = total - detected
            rate = detected / total * 100

            st.success("전체 변이 분석 완료!")

            col1, col2, col3 = st.columns(3)

            col1.metric("전체 변이", f"{total:,}개")
            col2.metric("구별 가능", f"{detected:,}개")
            col3.metric("구별 불가능", f"{undetected:,}개")

            st.metric(
                "이론적 변이 구별 가능 비율",
                f"{rate:.2f}%"
            )

            # 변이 검출 가능 비율 시각화
            
            
            
            
            
            
            
            
            
            
            
            
            st.subheader("6. 변이 구별 가능성 시각화")

            import pandas as pd

            chart_data = pd.DataFrame({
                "구분": ["구별 가능", "구별 불가능"],
                "변이 수": [detected, undetected]
            })

            st.bar_chart(
                chart_data,
                x="구분",
                y="변이 수",
                color="#46B5C7",
                horizontal=True
            )

            st.write("**전체 변이 중 구별 가능한 비율**")

            st.progress(
                rate / 100,
                text=f"{rate:.2f}%"
            )

            st.caption(
                "제한효소 절단 조각의 크기 변화를 기준으로 "
                "계산한 이론적 구별 가능 비율입니다."
            )
            st.metric(
                "이론적 변이 구별 가능 비율",
                f"{rate:.2f}%"
            )







        st.divider()
        st.subheader("7. 제한효소별 변이 구별 능력 비교")

        st.write(
            "EcoRI, BamHI, HindIII의 인식 부위가 각각 "
            "3개씩 포함된 3000bp 가상 플라스미드를 이용하여 "
            "단일 염기 치환에 대한 구별 가능성을 비교합니다."
        )

        if st.button("🔬 제한효소 3종 비교하기"):

            import pandas as pd

            # 비교용 가상 플라스미드 생성
            comparison_dna = list("A" * 3000)

            comparison_sites = {
                "EcoRI": ("GAATTC", [100, 900, 2100]),
                "BamHI": ("GGATCC", [300, 1300, 2300]),
                "HindIII": ("AAGCTT", [500, 1500, 2500])
            }

            for name, (sequence, positions) in comparison_sites.items():
                for pos in positions:
                    comparison_dna[pos:pos+6] = list(sequence)

            comparison_dna = "".join(comparison_dna)

            comparison_results = []

            with st.spinner("세 제한효소의 변이를 분석하는 중입니다..."):

                for name, (enzyme, positions) in comparison_sites.items():

                    original_pattern = get_pattern(
                        comparison_dna, enzyme
                    )

                    detected_count = 0
                    total_count = 0

                    for i in range(len(comparison_dna)):
                        for base in "ACGT":

                            if base == comparison_dna[i]:
                                continue

                            mutant = (
                                comparison_dna[:i]
                                + base
                                + comparison_dna[i+1:]
                            )

                            mutant_pattern = get_pattern(
                                mutant, enzyme
                            )

                            total_count += 1

                            if mutant_pattern != original_pattern:
                                detected_count += 1

                    rate_percent = detected_count / total_count * 100

                    comparison_results.append({
                        "제한효소": name,
                        "구별 가능한 변이": detected_count,
                        "전체 변이": total_count,
                        "구별 가능 비율 (%)": round(rate_percent, 2)
                    })

            st.success("제한효소 비교 분석 완료!")

            comparison_df = pd.DataFrame(comparison_results)

            st.dataframe(
                comparison_df,
                hide_index=True,
                use_container_width=True
            )

            st.subheader("제한효소별 비교 그래프")

            st.bar_chart(
                comparison_df,
                x="제한효소",
                y="구별 가능 비율 (%)",
                horizontal=True
            )

            st.caption(
                "각 효소의 인식 부위를 3개씩 배치한 "
                "가상 DNA를 대상으로 한 계산 결과입니다. "
                "실제 전기영동의 검출 한계는 반영하지 않았습니다."
            )
