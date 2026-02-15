"""
VHDL 도메인 데이터 클래스.
Port, Entity 등 파서/Export 공통 자료구조 정의.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Port:
    """단일 포트: 이름, 방향, 타입, 비트 폭."""
    name: str
    direction: str   # "in" | "out" | "inout" | "buffer"
    type: str        # "std_logic" | "std_logic_vector" 등
    width: int       # std_logic=1, vector=비트 수

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "direction": self.direction,
            "type": self.type,
            "width": self.width,
        }


@dataclass
class Entity:
    """Entity 블록: 모듈 이름 + 포트 목록."""
    module_name: str
    ports: List[Port] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "module_name": self.module_name,
            "ports": [p.to_dict() for p in self.ports],
        }
