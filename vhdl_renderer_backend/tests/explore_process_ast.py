"""process 포함 VHDL의 AST 노드 타입 확인."""
from tree_sitter import Language, Parser
from tree_sitter_vhdl import language

Lang = Language(language())
p = Parser(Lang)
code = b"""
entity R is port ( CLK : in std_logic; Q : out std_logic ); end entity;
architecture rtl of R is
  signal q : std_logic;
begin
  process (CLK) is
  begin
    if rising_edge(CLK) then q <= '1'; end if;
  end process;
end architecture;
"""
tree = p.parse(code)

def walk(n, depth=0, src=code):
    text = src[n.start_byte : n.end_byte].decode("utf-8", "replace").replace("\n", " ")[:55]
    print("  " * depth + n.type + ("  | " + repr(text) if text.strip() else ""))
    for c in n.children:
        walk(c, depth + 1, src)

walk(tree.root_node)
