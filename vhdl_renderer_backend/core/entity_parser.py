"""
Entity 파서: 정제된 VHDL에서 entity 이름과 port 목록 추출.
Input: 정제된 VHDL 텍스트 → Output: Entity 데이터 모델.
"""
import re
from typing import List, Optional

try:
    from ..models.vhdl_types import Entity, Port
except ImportError:
    from models.vhdl_types import Entity, Port


# entity 이름: entity \s+ <name> \s+ is
ENTITY_NAME_RE = re.compile(
    r"\bentity\s+(\w+)\s+is",
    re.IGNORECASE
)

# port ( ... );  괄호 짝 맞춰서 블록 추출
PORT_BLOCK_RE = re.compile(
    r"\bport\s*\(",
    re.IGNORECASE
)


def parse_entity(vhdl_text: str) -> Optional[Entity]:
    """
    정제된 VHDL 텍스트에서 첫 번째 entity 블록을 찾아 모듈 이름과 port 목록을 추출한다.

    Args:
        vhdl_text: 전처리된(주석 제거 등) VHDL 문자열

    Returns:
        Entity 인스턴스. entity/port를 찾지 못하면 None 또는 불완전한 Entity.
    """
    if not vhdl_text or not vhdl_text.strip():
        return None

    # 1) entity 이름 추출
    match = ENTITY_NAME_RE.search(vhdl_text)
    if not match:
        return None
    module_name = match.group(1)

    # 2) port ( ... ); 블록 내용 추출 (괄호 밸런스)
    port_start = PORT_BLOCK_RE.search(vhdl_text)
    if not port_start:
        return Entity(module_name=module_name, ports=[])

    start = port_start.end()
    depth = 1
    i = start
    while i < len(vhdl_text) and depth > 0:
        c = vhdl_text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        i += 1
    port_block = vhdl_text[start : i - 1].strip()

    # 3) 포트 선언 파싱 (; 로 구분, 쉼표는 레벨 0에서만 구분자로 사용하지 않고 ; 로만 구분)
    ports = _parse_port_declarations(port_block)

    return Entity(module_name=module_name, ports=ports)


def _parse_port_declarations(port_block: str) -> List[Port]:
    """port 블록 문자열을 파싱하여 Port 리스트 반환."""
    ports = []
    # 괄호 깊이 0인 세미콜론으로 선언 단위 분리
    decls = _split_top_level(port_block, ";")
    for decl in decls:
        decl = decl.strip()
        if not decl:
            continue
        port = _parse_single_port(decl)
        if port:
            ports.append(port)
    return ports


def _split_top_level(text: str, sep: str) -> List[str]:
    """괄호 밸런스를 유지하면서 sep 로만 최상위 분리."""
    parts = []
    depth = 0
    start = 0
    i = 0
    while i <= len(text) - len(sep):
        if text[i] in "()":
            if text[i] == "(":
                depth += 1
            else:
                depth -= 1
            i += 1
            continue
        if depth == 0 and text[i : i + len(sep)] == sep:
            parts.append(text[start:i].strip())
            start = i + len(sep)
            i = start
            continue
        i += 1
    if start <= len(text):
        parts.append(text[start:].strip())
    return parts


def _parse_single_port(decl: str) -> Optional[Port]:
    """
    단일 포트 선언 파싱.
    예: "A : in std_logic" / "DATA : out std_logic_vector(7 downto 0)"
    """
    # 첫 번째 " : " 로 이름과 (direction type...) 분리
    if ":" not in decl:
        return None
    name_part, rest = decl.split(":", 1)
    name = name_part.strip()
    rest = rest.strip()
    if not name or not rest:
        return None

    # direction: in | out | inout | buffer
    direction = ""
    for d in ("inout", "buffer", "in", "out"):
        if rest.lower().startswith(d + " ") or rest.lower().startswith(d + "\t"):
            direction = d.lower()
            rest = rest[len(d):].strip()
            break
    if not direction:
        return None

    # type + optional ( ... )  → type 이름과 width 추출
    type_name, width = _parse_port_type(rest)
    if not type_name:
        type_name = rest.split()[0] if rest.split() else "unknown"

    return Port(name=name, direction=direction, type=type_name, width=width or 1)


def _parse_port_type(rest: str) -> tuple:
    """'std_logic' -> ('std_logic', 1), 'std_logic_vector(7 downto 0)' -> ('std_logic_vector', 8)."""
    rest = rest.strip()
    # std_logic_vector ( N downto M ) → width = N - M + 1
    vec_match = re.match(
        r"(\w+)\s*\(\s*(\d+)\s+downto\s+(\d+)\s*\)",
        rest,
        re.IGNORECASE
    )
    if vec_match:
        type_name = vec_match.group(1)
        high, low = int(vec_match.group(2)), int(vec_match.group(3))
        width = high - low + 1
        return type_name, max(1, width)

    # std_logic_vector ( N to M )
    vec_to = re.match(
        r"(\w+)\s*\(\s*(\d+)\s+to\s+(\d+)\s*\)",
        rest,
        re.IGNORECASE
    )
    if vec_to:
        type_name = vec_to.group(1)
        low, high = int(vec_to.group(2)), int(vec_to.group(3))
        width = high - low + 1
        return type_name, max(1, width)

    # 단순 타입 (std_logic, bit 등)
    simple = re.match(r"(\w+)", rest)
    if simple:
        return simple.group(1), 1
    first_word = rest.split()[0] if rest.split() else "unknown"
    return first_word, 1
