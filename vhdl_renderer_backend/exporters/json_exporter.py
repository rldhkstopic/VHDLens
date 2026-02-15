"""
데이터 모델 → JSON 파일. 웹 프론트엔드 / VS Code Webview 연동용.
"""
import json
from pathlib import Path
from typing import Any, Union


def export_json(data: Any, output_path: Union[str, Path]) -> str:
    """
    파이썬 데이터 모델을 JSON 파일로 저장한다.

    Args:
        data: to_dict() 를 지원하는 객체 또는 dict
        output_path: 저장 경로

    Returns:
        저장된 파일 경로 문자열
    """
    if hasattr(data, "to_dict"):
        data = data.to_dict()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return str(path.resolve())
