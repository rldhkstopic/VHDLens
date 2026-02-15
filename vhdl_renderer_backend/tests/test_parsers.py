"""
전처리기 및 Entity 파서 단위 테스트 (pytest).
"""
import pytest
from pathlib import Path

# 프로젝트 루트에서 pytest 시 상위 경로에 backend 가 있음
try:
    from vhdl_renderer_backend.core import preprocess, parse_entity
    from vhdl_renderer_backend.models import Entity, Port
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core import preprocess, parse_entity
    from models import Entity, Port


DIR = Path(__file__).resolve().parent / "test_data"


def test_preprocess_removes_comments():
    raw = "entity Foo is\n  port ( A : in std_logic );  -- comment\nend;"
    out = preprocess(raw, normalize_whitespace=True)
    assert "--" not in out
    assert "comment" not in out
    assert "Foo" in out and "port" in out


def test_preprocess_preserves_entity_port():
    raw = "entity AND_GATE is port ( A : in std_logic; B : in std_logic; Y : out std_logic ); end;"
    out = preprocess(raw)
    assert "AND_GATE" in out and "port" in out and "std_logic" in out


def test_parse_entity_and_gate():
    path = DIR / "and_gate.vhd"
    if not path.exists():
        pytest.skip("test_data/and_gate.vhd not found")
    text = path.read_text(encoding="utf-8")
    cleaned = preprocess(text)
    entity = parse_entity(cleaned)
    assert entity is not None
    assert entity.module_name == "AND_GATE"
    assert len(entity.ports) == 3
    names = {p.name for p in entity.ports}
    assert names == {"A", "B", "Y"}
    a = next(p for p in entity.ports if p.name == "A")
    assert a.direction == "in" and a.type == "std_logic" and a.width == 1
    y = next(p for p in entity.ports if p.name == "Y")
    assert y.direction == "out"


def test_parse_entity_register_8bit():
    path = DIR / "register_8bit.vhd"
    if not path.exists():
        pytest.skip("test_data/register_8bit.vhd not found")
    text = path.read_text(encoding="utf-8")
    cleaned = preprocess(text)
    entity = parse_entity(cleaned)
    assert entity is not None
    assert entity.module_name == "REGISTER_8BIT"
    d = next(p for p in entity.ports if p.name == "D")
    assert d.width == 8 and "vector" in d.type.lower()
    q = next(p for p in entity.ports if p.name == "Q")
    assert q.width == 8


def test_parse_entity_vhdl_project_top():
    """복합 프로젝트 탑레벨: UART, 메모리, LED, SPI, inout 등 다양한 포트."""
    path = DIR / "vhdl_project" / "top.vhd"
    if not path.exists():
        pytest.skip("test_data/vhdl_project/top.vhd not found")
    text = path.read_text(encoding="utf-8")
    cleaned = preprocess(text)
    entity = parse_entity(cleaned)
    assert entity is not None
    assert entity.module_name == "top"
    port_names = {p.name for p in entity.ports}
    assert "CLK_50" in port_names and "RST_N" in port_names
    assert "UART_TX" in port_names and "UART_RX" in port_names
    assert "LED" in port_names
    assert "MEM_ADDR" in port_names or "MEM_DQ" in port_names
    assert "SPI_MOSI" in port_names and "SPI_MISO" in port_names
    assert "DBG_GPIO" in port_names
    inout_ports = [p for p in entity.ports if p.direction == "inout"]
    assert any(p.name == "MEM_DQ" for p in inout_ports)
    assert any(p.name == "DBG_GPIO" for p in inout_ports)
    assert len(entity.ports) >= 15
