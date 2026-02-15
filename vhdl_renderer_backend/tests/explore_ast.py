"""AST 노드 구조 확인용 일회성 스크립트."""
from tree_sitter import Language, Parser
from tree_sitter_vhdl import language

Lang = Language(language())
p = Parser(Lang)
code = b"""
entity AND_GATE is
  port (
    A : in std_logic;
    B : in std_logic;
    Y : out std_logic
  );
end entity AND_GATE;
"""
tree = p.parse(code)


def walk(n, depth=0, src=code):
    text = src[n.start_byte : n.end_byte].decode("utf-8", "replace").replace("\n", " ")[:50]
    print("  " * depth + n.type + ("  | " + repr(text) if text.strip() else ""))
    for c in n.children:
        walk(c, depth + 1, src)


walk(tree.root_node)
