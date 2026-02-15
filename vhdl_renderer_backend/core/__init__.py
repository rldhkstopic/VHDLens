from .preprocessor import preprocess
from .entity_parser import parse_entity

__all__ = ["preprocess", "parse_entity"]

try:
    from .ast_parser import parse_to_tree, ast_to_dict, ast_dump_json, extract_entity_ports_from_tree, parse_vhdl
    __all__ = list(__all__) + ["parse_to_tree", "ast_to_dict", "ast_dump_json", "extract_entity_ports_from_tree", "parse_vhdl"]
except ImportError:
    pass
