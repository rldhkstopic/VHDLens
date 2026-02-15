"""
VHDL 파일을 Tree-sitter로 파싱하여 AST 전체를 JSON 파일로 덤프.
사용: python run_ast_dump.py <file.vhd> [output_ast_tree.json]
"""
import sys
from pathlib import Path

try:
    from vhdl_renderer_backend.core.ast_parser import parse_to_tree, ast_dump_json, extract_entity_ports_from_tree
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.ast_parser import parse_to_tree, ast_dump_json, extract_entity_ports_from_tree

def main():
    if len(sys.argv) < 2:
        print("사용: python run_ast_dump.py <file.vhd> [output.json]", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else path.parent / "output_ast_tree.json"
    if not path.exists():
        print(f"파일 없음: {path}", file=sys.stderr)
        sys.exit(1)
    code = path.read_text(encoding="utf-8", errors="replace")
    tree = parse_to_tree(code)
    entity = extract_entity_ports_from_tree(tree, code)
    json_str = ast_dump_json(tree, code)
    out_path.write_text(json_str, encoding="utf-8")
    print(f"AST 노드 수(대략): {tree.root_node.descendant_count}")
    if entity:
        print(f"Entity: {entity.module_name}, Ports: {len(entity.ports)}")
    print(f"저장: {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
