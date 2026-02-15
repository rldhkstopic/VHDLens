"""
VHDL 전처리기: 주석 제거 및 텍스트 정규화.
Input: 원본 VHDL 문자열 → Output: 정제된 VHDL 문자열.
"""
import re


def preprocess(vhdl_text: str, normalize_whitespace: bool = True) -> str:
    """
    VHDL 소스에서 주석을 제거하고, 선택적으로 공백을 정규화한다.

    - `--` 부터 해당 줄 끝까지 제거 (인라인 주석 포함).
    - normalize_whitespace=True 이면 연속 공백/탭/줄바꿈을 단일 공백으로 치환.

    Args:
        vhdl_text: 원본 VHDL 텍스트
        normalize_whitespace: True면 공백 정규화 수행 (기본 True)

    Returns:
        정제된 VHDL 텍스트
    """
    if not vhdl_text or not vhdl_text.strip():
        return vhdl_text

    # 1) 줄 단위로 -- 부터 끝까지 제거 (문자열 내 -- 는 고려하지 않음; VHDL에서는 "--" 가 문자열 안에 올 수 있으나 1단계에서는 단순화)
    lines = vhdl_text.split("\n")
    stripped = []
    for line in lines:
        # VHDL 주석: -- 이후 제거. 따옴표 안의 -- 는 보존하려면 복잡해지므로, 여기서는 첫 번째 -- 부터 제거
        idx = _find_comment_start(line)
        if idx >= 0:
            line = line[:idx]
        stripped.append(line)

    text = "\n".join(stripped)

    if normalize_whitespace:
        # 연속 공백·탭·줄바꿈을 단일 공백으로 (줄 구조는 무시하고 한 덩어리로 만듦)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

    return text


def _find_comment_start(line: str) -> int:
    """
    줄에서 주석 시작 위치(--)를 찾는다.
    단순 버전: 문자열 리터럑 내부의 -- 는 구분하지 않고, 첫 -- 의 인덱스를 반환.
    """
    i = 0
    in_double = False
    in_single = False
    while i < len(line):
        c = line[i]
        if c == '"' and not in_single:
            in_double = not in_double
            i += 1
            continue
        if c == "'" and not in_double:
            in_single = not in_single
            i += 1
            continue
        if not in_double and not in_single and i + 1 < len(line) and line[i : i + 2] == "--":
            return i
        i += 1
    return -1
