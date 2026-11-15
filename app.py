
import streamlit as st
from dna_analysis import analyze_plasmid, get_pattern
st.set_page_config(
    page_title="플라스미드 DNA 시뮬레이터",
    page_icon="🧬",
    layout="wide"
)

# 모든 분석 결과를 저장할 공통 공간
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = {}

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
            st.session_state["show_comparison"] = True

        if st.session_state.get("show_comparison", False):

            mutant_dna = (
                current_dna[:mut_pos - 1]
                + new_base
                + current_dna[mut_pos:]
            )


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
            st.session_state["show_mutation_analysis"] = True

        if st.session_state.get("show_mutation_analysis", False):

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

        st.divider()
        st.subheader("8. 제한효소 3종의 분석 결과 종합")

        st.write(
            "각 제한효소로 별도로 분석했을 때 "
            "구별 가능한 변이들을 합쳐 "
            "전체 변이 구별 가능성을 계산합니다."
        )

        if st.button("🧬 세 효소 종합 분석하기"):

            import pandas as pd

            # 39단계와 동일한 가상 플라스미드
            joint_dna = list("A" * 3000)

            joint_sites = {
                "EcoRI": ("GAATTC", [100, 900, 2100]),
                "BamHI": ("GGATCC", [300, 1300, 2300]),
                "HindIII": ("AAGCTT", [500, 1500, 2500])
            }

            for name, (sequence, positions) in joint_sites.items():
                for pos in positions:
                    joint_dna[pos:pos+6] = list(sequence)

            joint_dna = "".join(joint_dna)

            # 원본 DNA 절단 패턴
            reference_patterns = {}

            for name, (enzyme, positions) in joint_sites.items():
                reference_patterns[name] = get_pattern(
                    joint_dna, enzyme
                )

            # 각 효소가 구별한 변이 저장
            detected_by = {
                name: set() for name in joint_sites
            }

            with st.spinner("세 효소의 분석 결과를 종합하는 중입니다..."):

                for i in range(len(joint_dna)):
                    for base in "ACGT":

                        if base == joint_dna[i]:
                            continue

                        mutant = (
                            joint_dna[:i]
                            + base
                            + joint_dna[i+1:]
                        )

                        for name, (enzyme, positions) in joint_sites.items():

                            mutant_pattern = get_pattern(
                                mutant, enzyme
                            )

                            if mutant_pattern != reference_patterns[name]:
                                detected_by[name].add((i+1, base))

            # 각 효소의 구별 가능 변이 합집합
            combined = set()

            for mutations in detected_by.values():
                combined.update(mutations)

            total = len(joint_dna) * 3
            combined_count = len(combined)
            combined_rate = combined_count / total * 100

            st.success("종합 분석 완료!")

            rows = []

            for name, mutations in detected_by.items():
                rows.append({
                    "분석 방식": name,
                    "구별 가능 변이 수": len(mutations)
                })

            rows.append({
                "분석 방식": "3종 결과 종합",
                "구별 가능 변이 수": combined_count
            })

            result_df = pd.DataFrame(rows)

            st.dataframe(
                result_df,
                hide_index=True,
                use_container_width=True
            )

            st.subheader("종합 분석 결과")

            col1, col2 = st.columns(2)

            col1.metric(
                "구별 가능한 변이",
                f"{combined_count:,}개"
            )

            col2.metric(
                "이론적 구별 가능 비율",
                f"{combined_rate:.2f}%"
            )

            st.bar_chart(
                result_df,
                x="분석 방식",
                y="구별 가능 변이 수",
                horizontal=True
            )

            st.caption(
                "세 제한효소를 각각 따로 사용한 분석 결과를 "
                "종합한 것입니다. 실제 전기영동의 분리능이나 "
                "동시 절단 실험을 재현한 결과는 아닙니다."
            )

        st.divider()
        st.subheader("9. DNA 변이 위치별 구별 가능성 분석")

        st.write(
            "현재 입력한 DNA의 각 위치에서 가능한 단일 염기 "
            "치환을 분석하고, 절단 패턴이 달라지는 위치를 "
            "그래프로 표시합니다."
        )

        if st.button("📍 변이 위치별 분석하기"):

            target_dna = "".join(dna.upper().split())
            target_enzyme = enzymes[selected]

            original_pattern = get_pattern(
                target_dna, target_enzyme
            )

            detected_positions = []

            with st.spinner("DNA 위치별 변이를 분석하는 중입니다..."):

                for i in range(len(target_dna)):

                    detected_count = 0

                    for base in "ACGT":

                        if base == target_dna[i]:
                            continue

                        mutant = (
                            target_dna[:i]
                            + base
                            + target_dna[i+1:]
                        )

                        mutant_pattern = get_pattern(
                            mutant, target_enzyme
                        )

                        if mutant_pattern != original_pattern:
                            detected_count += 1

                    if detected_count > 0:
                        detected_positions.append({
                            "DNA 위치 (bp)": i + 1,
                            "구별 가능한 치환 수": detected_count
                        })

            # 다른 버튼을 눌러도 결과가 유지되도록 저장
            st.session_state["position_analysis"] = {
                "dna": target_dna,
                "enzyme": target_enzyme,
                "positions": detected_positions
            }

        saved = st.session_state.get("position_analysis")

        if (
            saved is not None
            and saved["dna"] == "".join(dna.upper().split())
            and saved["enzyme"] == enzymes[selected]
        ):

            import pandas as pd

            positions = saved["positions"]

            total_detected = sum(
                item["구별 가능한 치환 수"]
                for item in positions
            )

            st.success("변이 위치별 분석 완료!")

            col1, col2 = st.columns(2)

            col1.metric(
                "구별 가능한 변이 위치",
                f"{len(positions)}곳"
            )

            col2.metric(
                "구별 가능한 단일 염기 치환",
                f"{total_detected}개"
            )

            if positions:

                position_df = pd.DataFrame(positions)

                st.subheader("변이 위치별 분석 그래프")

                st.scatter_chart(
                    position_df,
                    x="DNA 위치 (bp)",
                    y="구별 가능한 치환 수",
                    color="#46B5C7",
                    size=100
                )

                st.subheader("구별 가능한 변이 위치 목록")

                st.dataframe(
                    position_df,
                    hide_index=True,
                    use_container_width=True
                )

            else:
                st.info(
                    "현재 조건에서 절단 패턴이 달라지는 "
                    "단일 염기 치환을 찾지 못했습니다."
                )

            st.caption(
                "제한효소 절단 패턴의 차이를 기준으로 한 "
                "이론적 분석입니다. 실제 전기영동의 "
                "밴드 분리능은 반영하지 않았습니다."
            )

        st.divider()
        st.subheader("10. 변이에 따른 제한효소 인식 부위 변화")

        st.write(
            "4번 항목에서 설정한 변이 위치와 변경 염기를 이용해 "
            "염기서열 및 제한효소 인식 부위의 변화를 분석합니다."
        )

        if st.checkbox(
            "🔎 변이 전후 염기서열 분석 결과 보기",
            key="show_sequence_details"
        ):

            original_dna = "".join(dna.upper().split())
            enzyme = enzymes[selected]

            # 앞에서 선택한 변이 적용
            index = mut_pos - 1

            mutated_dna = (
                original_dna[:index]
                + new_base
                + original_dna[index+1:]
            )

            st.write(
                f"**변이 내용:** {mut_pos}번째 염기 "
                f"{original_dna[index]} → {new_base}"
            )

            # 변이 전후 주변 염기서열 표시
            start = max(0, index - 7)
            end = min(len(original_dna), index + 8)

            original_view = (
                original_dna[start:index]
                + "[" + original_dna[index] + "]"
                + original_dna[index+1:end]
            )

            mutated_view = (
                mutated_dna[start:index]
                + "[" + mutated_dna[index] + "]"
                + mutated_dna[index+1:end]
            )

            st.write("**원본 DNA 주변 서열**")
            st.code(original_view)

            st.write("**변이 DNA 주변 서열**")
            st.code(mutated_view)

            # 원형 DNA의 제한효소 인식 부위 찾기
            def find_recognition_sites(sequence, motif):
                circular = sequence + sequence[:len(motif)-1]

                return {
                    i for i in range(len(sequence))
                    if circular[i:i+len(motif)] == motif
                }

            original_sites = find_recognition_sites(
                original_dna, enzyme
            )

            mutated_sites = find_recognition_sites(
                mutated_dna, enzyme
            )

            lost_sites = sorted(
                original_sites - mutated_sites
            )

            gained_sites = sorted(
                mutated_sites - original_sites
            )

            st.subheader("제한효소 인식 부위 분석")

            st.write(
                f"**사용한 효소:** {selected} ({enzyme})"
            )

            if lost_sites:

                for pos in lost_sites:

                    changed_motif = "".join(
                        mutated_dna[(pos+j) % len(mutated_dna)]
                        for j in range(len(enzyme))
                    )

                    st.warning(
                        f"{pos+1}번에서 시작하는 인식 부위 소실: "
                        f"{enzyme} → {changed_motif}"
                    )

            if gained_sites:

                for pos in gained_sites:

                    st.success(
                        f"{pos+1}번에서 시작하는 "
                        f"새로운 인식 부위 생성: {enzyme}"
                    )

            if not lost_sites and not gained_sites:

                st.info(
                    "이번 변이로 생성되거나 사라진 "
                    "제한효소 인식 부위가 없습니다."
                )

            # 절단 패턴 변화 확인
            original_pattern = get_pattern(
                original_dna, enzyme
            )

            mutated_pattern = get_pattern(
                mutated_dna, enzyme
            )

            st.write("**원본 절단 패턴:**", original_pattern)
            st.write("**변이 절단 패턴:**", mutated_pattern)

            if original_pattern != mutated_pattern:

                st.success(
                    "인식 부위 변화에 따라 절단 패턴이 달라졌습니다."
                )

            else:

                st.info(
                    "이번 변이에서는 절단 조각 크기 패턴이 동일합니다."
                )

            st.caption(
                "원형 DNA 서열과 제한효소의 완전 절단을 "
                "가정한 이론적 분석 결과입니다."
            )
