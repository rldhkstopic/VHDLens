"""
Tree-sitter 기반 AST 파서.
VHDL 원문 → AST 구축, 전체 덤프(JSON), Entity/Port 세분화 추출.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

try:
    from tree_sitter import Language, Parser, Tree, Node
    from tree_sitter_vhdl import language as vhdl_language
except ImportError:
    Language = Parser = Tree = Node = None
    vhdl_language = None

try:
    from ..models.vhdl_types import Entity, Port
except ImportError:
    from models.vhdl_types import Entity, Port


def _get_parser() -> Parser:
    if Parser is None or vhdl_language is None:
        raise RuntimeError("tree-sitter, tree-sitter-vhdl 패키지가 필요합니다. pip install tree-sitter tree-sitter-vhdl")
    lang = Language(vhdl_language())
    p = Parser(lang)
    return p


def parse_to_tree(vhdl_source: str) -> Tree:
    """VHDL 소스를 파싱하여 Tree-sitter AST(Tree) 반환."""
    parser = _get_parser()
    if isinstance(vhdl_source, str):
        vhdl_source = vhdl_source.encode("utf-8")
    return parser.parse(vhdl_source)


def _node_to_dict(node: Node, source: bytes) -> Dict[str, Any]:
    """단일 노드를 type, range, text, children 포함한 dict로 변환."""
    text = source[node.start_byte : node.end_byte].decode("utf-8", "replace")
    d: Dict[str, Any] = {
        "type": node.type,
        "start_byte": node.start_byte,
        "end_byte": node.end_byte,
        "text": text.strip() if len(text) < 120 else text.strip()[:117] + "...",
    }
    if node.child_count > 0:
        d["children"] = [_node_to_dict(c, source) for c in node.children]
    return d


def ast_to_dict(tree: Tree, source: str) -> Dict[str, Any]:
    """전체 AST를 JSON 직렬화 가능한 dict로 변환 (Full Dump)."""
    if isinstance(source, str):
        source = source.encode("utf-8")
    return _node_to_dict(tree.root_node, source)


def ast_dump_json(tree: Tree, source: str, indent: int = 2) -> str:
    """AST 전체를 JSON 문자열로 덤프."""
    return json.dumps(ast_to_dict(tree, source), ensure_ascii=False, indent=indent)


def _find_first(node: Node, typ: str) -> Optional[Node]:
    """자식 중 type이 typ인 첫 노드."""
    for c in node.children:
        if c.type == typ:
            return c
        found = _find_first(c, typ)
        if found:
            return found
    return None


def _find_all(node: Node, typ: str) -> List[Node]:
    """node 서브트리에서 type이 typ인 모든 노드 (자신 포함)."""
    out: List[Node] = []
    if node.type == typ:
        out.append(node)
    for c in node.children:
        out.extend(_find_all(c, typ))
    return out


def _text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", "replace").strip()


def _get_identifier_name(node: Node, source: bytes) -> str:
    """identifier 노드 또는 identifier_list 내 첫 identifier 텍스트."""
    ident = _find_first(node, "identifier")
    if ident:
        return _text(ident, source)
    return _text(node, source)


def _get_mode(node: Optional[Node], source: bytes) -> str:
    """simple_mode_indication 등에서 mode(in/out/inout/buffer) 추출."""
    if not node:
        return "in"
    mode_node = _find_first(node, "mode")
    if not mode_node:
        return "in"
    for child in mode_node.children:
        t = child.type
        if t in ("in", "out", "inout", "buffer"):
            return t
    return "in"


def _get_subtype_type_and_width(node: Node, source: bytes) -> tuple[str, int]:
    """subtype_indication 노드에서 타입명과 비트 폭 추출. std_logic -> (std_logic, 1), vector(N downto M) -> (std_logic_vector, N-M+1)."""
    text = _text(node, source)
    # array_type_definition 또는 name ( range ) 형태 처리
    # 간단히: "std_logic" -> 1, "std_logic_vector(7 downto 0)" -> 8
    import re
    vec_match = re.search(r"(\w+)\s*\(\s*(\d+)\s+downto\s+(\d+)\s*\)", text, re.IGNORECASE)
    if vec_match:
        name, high, low = vec_match.group(1), int(vec_match.group(2)), int(vec_match.group(3))
        return name, max(1, high - low + 1)
    vec_to = re.search(r"(\w+)\s*\(\s*(\d+)\s+to\s+(\d+)\s*\)", text, re.IGNORECASE)
    if vec_to:
        name, low, high = vec_to.group(1), int(vec_to.group(2)), int(vec_to.group(3))
        return name, max(1, high - low + 1)
    # 단순 타입
    simple = re.match(r"(\w+)", text)
    if simple:
        return simple.group(1), 1
    return text or "unknown", 1


def extract_entity_ports_from_tree(tree: Tree, source: str) -> Optional[Entity]:
    """AST에서 첫 entity_declaration을 찾아 Entity(이름, ports) 반환."""
    if isinstance(source, str):
        source_bytes = source.encode("utf-8")
    else:
        source_bytes = source
    root = tree.root_node
    entity_decl = _find_first(root, "entity_declaration")
    if not entity_decl:
        return None
    # entity 이름: entity_declaration > identifier (두 번째는 end 쪽일 수 있음; entity_head 쪽 identifier가 선언 이름)
    ident_node = _find_first(entity_decl, "identifier")
    if not ident_node:
        return None
    module_name = _text(ident_node, source_bytes)
    # end entity XXX 에서 이름이 나오므로, 첫 identifier가 보통 선언 이름
    head = _find_first(entity_decl, "entity_head")
    if head:
        port_clause = _find_first(head, "port_clause")
        if port_clause:
            interface_list = _find_first(port_clause, "interface_list")
            if interface_list:
                ports: List[Port] = []
                for iface in _find_all(interface_list, "interface_declaration"):
                    name = _get_identifier_name(iface, source_bytes)
                    mode_ind = _find_first(iface, "simple_mode_indication")
                    if not mode_ind:
                        mode_ind = _find_first(iface, "mode_indication")
                    direction = _get_mode(mode_ind, source_bytes) if mode_ind else "in"
                    subtype = _find_first(iface, "subtype_indication")
                    type_name, width = _get_subtype_type_and_width(subtype, source_bytes) if subtype else ("unknown", 1)
                    ports.append(Port(name=name, direction=direction, type=type_name, width=width))
                return Entity(module_name=module_name, ports=ports)
    return Entity(module_name=module_name, ports=[])


def parse_vhdl(vhdl_source: str, extract_entity: bool = True) -> Dict[str, Any]:
    """
    한 번에 파싱 + (선택) Entity 추출.
    Returns:
        {"tree": Tree, "ast_dict": dict (JSON 가능), "entity": Entity or None}
        참고: "tree"는 JSON 직렬화 불가; 덤프 시 ast_dict만 사용.
    """
    tree = parse_to_tree(vhdl_source)
    out: Dict[str, Any] = {"ast_dict": ast_to_dict(tree, vhdl_source)}
    if extract_entity:
        out["entity"] = extract_entity_ports_from_tree(tree, vhdl_source)
    out["tree"] = tree  # 프로그램용; json.dumps 시 제외 필요
    return out
