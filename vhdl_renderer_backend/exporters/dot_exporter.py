"""
파서 결과 → Graphviz DOT/이미지. 시각적 디버깅용.
(1단계 스켈레톤 — graph_model 연동 후 구현)
"""
from pathlib import Path
from typing import Any, Union


def export_dot(data: Any, output_path: Union[str, Path], format: str = "png") -> str:
    """
    데이터 모델을 Graphviz로 렌더링하여 파일로 저장한다.

    Args:
        data: Entity 등 데이터 모델
        output_path: 저장 경로 (확장자 없이 지정 시 format 으로 붙음)
        format: "png", "svg", "dot" 등

    Returns:
        저장된 파일 경로
    """
    # TODO: graphviz 라이브러리 연동, in/out 노드 배치
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    return str(Path(output_path).resolve())
