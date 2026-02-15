"""
Tree-sitter AST 파서 테스트.
- AST 구축 및 Full Dump
- Entity/Port 세분화 추출 (기존 entity_parser와 동일 결과 검증)
"""
import json
import pytest
from pathlib import Path

try:
    from vhdl_renderer_backend.core.preprocessor import preprocess
    from vhdl_renderer_backend.core.ast_parser import (
        parse_to_tree,
        ast_to_dict,
        ast_dump_json,
        extract_entity_ports_from_tree,
        parse_vhdl,
    )
    from vhdl_renderer_backend.core.entity_parser import parse_entity
    from vhdl_renderer_backend.models import Entity, Port
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.preprocessor import preprocess
    from core.ast_parser import (
        parse_to_tree,
        ast_to_dict,
        ast_dump_json,
        extract_entity_ports_from_tree,
        parse_vhdl,
    )
    from core.entity_parser import parse_entity
    from models import Entity, Port

DIR = Path(__file__).resolve().parent / "test_data"
MICRO = DIR / "micro"


def test_ast_parse_to_tree():
    """AST가 design_file 루트로 생성되는지."""
    code = "entity Foo is port ( A : in std_logic ); end entity;"
    tree = parse_to_tree(code)
    assert tree.root_node is not None
    assert tree.root_node.type == "design_file"


def test_ast_entity_declaration_found():
    """entity_declaration 노드가 트리에 존재하는지."""
    code = "entity AND_GATE is port ( A : in std_logic; Y : out std_logic ); end entity;"
    tree = parse_to_tree(code)
    d = ast_to_dict(tree, code)
    assert "children" in d
    types = [c["type"] for c in d["children"]]
    assert "design_unit" in types


def test_ast_dump_json_serializable():
    """AST 전체가 JSON 직렬화 가능한지."""
    code = "entity Foo is port ( X : in std_logic ); end entity;"
    tree = parse_to_tree(code)
    s = ast_dump_json(tree, code)
    loaded = json.loads(s)
    assert loaded["type"] == "design_file"


def test_ast_extract_entity_ports():
    """AST에서 Entity + Port 추출이 기존 entity_parser와 일치하는지."""
    code = """
    entity AND_GATE is
      port ( A : in std_logic; B : in std_logic; Y : out std_logic );
    end entity AND_GATE;
    """
    tree = parse_to_tree(code)
    entity = extract_entity_ports_from_tree(tree, code)
    assert entity is not None
    assert entity.module_name == "AND_GATE"
    assert len(entity.ports) == 3
    names = {p.name for p in entity.ports}
    assert names == {"A", "B", "Y"}
    y = next(p for p in entity.ports if p.name == "Y")
    assert y.direction == "out" and y.type == "std_logic" and y.width == 1


def test_ast_extract_std_logic_vector():
    """std_logic_vector(7 downto 0) 포트 폭 추출."""
    code = "entity REG is port ( D : in std_logic_vector(7 downto 0); Q : out std_logic_vector(7 downto 0) ); end entity;"
    tree = parse_to_tree(code)
    entity = extract_entity_ports_from_tree(tree, code)
    assert entity is not None
    d = next(p for p in entity.ports if p.name == "D")
    assert d.width == 8
    assert "vector" in d.type.lower() or d.type == "std_logic_vector"


def test_ast_vs_regex_entity_parity():
    """동일 소스에 대해 AST 추출 결과와 기존 regex entity_parser 결과가 동일한지."""
    path = DIR / "and_gate.vhd"
    if not path.exists():
        pytest.skip("and_gate.vhd not found")
    raw = path.read_text(encoding="utf-8")
    cleaned = preprocess(raw)
    regex_entity = parse_entity(cleaned)
    tree = parse_to_tree(cleaned)
    ast_entity = extract_entity_ports_from_tree(tree, cleaned)
    assert regex_entity is not None and ast_entity is not None
    assert regex_entity.module_name == ast_entity.module_name
    assert len(regex_entity.ports) == len(ast_entity.ports)
    for rp, ap in zip(regex_entity.ports, ast_entity.ports):
        assert rp.name == ap.name and rp.direction == ap.direction and rp.width == ap.width


def test_micro_entity_port():
    """마이크로 테스트: test_entity_port.vhd."""
    path = MICRO / "test_entity_port.vhd"
    if not path.exists():
        pytest.skip("micro/test_entity_port.vhd not found")
    code = path.read_text(encoding="utf-8")
    tree = parse_to_tree(code)
    entity = extract_entity_ports_from_tree(tree, code)
    assert entity is not None
    assert entity.module_name == "AND_GATE"
    assert len(entity.ports) == 3


def test_micro_std_logic_vector():
    """마이크로 테스트: test_std_logic_vector.vhd."""
    path = MICRO / "test_std_logic_vector.vhd"
    if not path.exists():
        pytest.skip("micro/test_std_logic_vector.vhd not found")
    code = path.read_text(encoding="utf-8")
    tree = parse_to_tree(code)
    entity = extract_entity_ports_from_tree(tree, code)
    assert entity is not None
    assert entity.module_name == "REG"
    d = next(p for p in entity.ports if p.name == "D")
    q = next(p for p in entity.ports if p.name == "Q")
    assert d.width == 8 and q.width == 8


def test_micro_signal_ast_has_architecture():
    """마이크로 테스트: signal 포함 파일에서 AST에 architecture 또는 signal 관련 노드 존재."""
    path = MICRO / "test_signal.vhd"
    if not path.exists():
        pytest.skip("micro/test_signal.vhd not found")
    code = path.read_text(encoding="utf-8")
    tree = parse_to_tree(code)
    d = ast_to_dict(tree, code)

    def has_type(obj, typ):
        if isinstance(obj, dict):
            if obj.get("type") == typ:
                return True
            for c in obj.get("children", []):
                if has_type(c, typ):
                    return True
        return False

    def has_text(obj, sub):
        if isinstance(obj, dict):
            if sub in obj.get("text", ""):
                return True
            for c in obj.get("children", []):
                if has_text(c, sub):
                    return True
        return False
    assert has_type(d, "entity_declaration")
    # grammar에 따라 architecture_definition 등
    assert has_type(d, "architecture_definition") or has_text(d, "architecture") or has_text(d, "signal")


def _ast_has_type(ast_dict, typ):
    """AST dict 서브트리에서 type이 typ인 노드 존재 여부."""
    if isinstance(ast_dict, dict):
        if ast_dict.get("type") == typ:
            return True
        for c in ast_dict.get("children", []):
            if _ast_has_type(c, typ):
                return True
    return False


def test_micro_process_ast_has_process_and_flow():
    """마이크로 테스트: process + 감지 목록 + if/elsif 동작 흐름 파싱."""
    path = MICRO / "test_process.vhd"
    if not path.exists():
        pytest.skip("micro/test_process.vhd not found")
    code = path.read_text(encoding="utf-8")
    tree = parse_to_tree(code)
    d = ast_to_dict(tree, code)
    assert _ast_has_type(d, "entity_declaration")
    assert _ast_has_type(d, "architecture_definition")
    assert _ast_has_type(d, "process_statement"), "process 블록이 AST에 있어야 함"
    assert _ast_has_type(d, "sensitivity_specification") or _ast_has_type(d, "sensitivity_list"), "감지 목록 파싱"
    assert _ast_has_type(d, "if_statement") or _ast_has_type(d, "if_statement_block"), "if 동작 흐름 파싱"
    assert _ast_has_type(d, "sequential_block"), "순차 구문 블록"
    entity = extract_entity_ports_from_tree(tree, code)
    assert entity is not None and entity.module_name == "REG" and len(entity.ports) == 4


def test_micro_process_fsm_ast_has_case_flow():
    """마이크로 테스트: process + FSM (case/when) 동작 흐름 파싱."""
    path = MICRO / "test_process_fsm.vhd"
    if not path.exists():
        pytest.skip("micro/test_process_fsm.vhd not found")
    code = path.read_text(encoding="utf-8")
    tree = parse_to_tree(code)
    d = ast_to_dict(tree, code)
    assert _ast_has_type(d, "process_statement")
    assert _ast_has_type(d, "sensitivity_specification") or _ast_has_type(d, "sensitivity_list")
    assert _ast_has_type(d, "case_statement") or _ast_has_type(d, "case_statement_block") or "case" in str(d), "case/when FSM 흐름"
    entity = extract_entity_ports_from_tree(tree, code)
    assert entity is not None and entity.module_name == "FSM" and len(entity.ports) == 4
