"""
프로그램 진입점 (CLI).
.vhd 파일 로드 → 전처리 → Entity(및 추후 Arch) 파싱 → JSON/Dot 출력.
"""
import argparse
import sys
from pathlib import Path

# 패키지 루트 기준 임포트 (실행: python -m vhdl_renderer_backend.main 또는 python main.py)
try:
    from vhdl_renderer_backend.core import preprocess, parse_entity
    from vhdl_renderer_backend.exporters.json_exporter import export_json
except ImportError:
    from core import preprocess, parse_entity
    from exporters.json_exporter import export_json


def main() -> int:
    parser = argparse.ArgumentParser(
        description="VHDL 파서 (1단계): Entity/Port 추출 후 JSON 출력"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="입력 .vhd 파일 경로",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="JSON 출력 경로 (기본: 입력파일과 동일 디렉터리 output.json)",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="공백 정규화 없이 주석만 제거",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"오류: 파일을 찾을 수 없습니다. {args.input}", file=sys.stderr)
        return 1

    text = args.input.read_text(encoding="utf-8", errors="replace")
    cleaned = preprocess(text, normalize_whitespace=not args.no_normalize)
    entity = parse_entity(cleaned)

    if entity is None:
        print("경고: entity를 찾지 못했습니다.", file=sys.stderr)
        out_path = args.output or args.input.parent / "output.json"
        export_json({"module_name": "", "ports": []}, out_path)
        print(f"빈 구조 저장: {out_path}")
        return 0

    out_path = args.output or args.input.parent / "output.json"
    export_json(entity, out_path)
    print(f"Entity: {entity.module_name}, Port 수: {len(entity.ports)}")
    print(f"저장: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
