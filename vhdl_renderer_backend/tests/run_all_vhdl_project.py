"""
vhdl_project/ 내 모든 .vhd 파일에 대해 파싱 실행.
각 파일의 첫 entity 이름·포트 수를 출력하고, 실패 시 종료 코드 1.
"""
import sys
from pathlib import Path

try:
    from vhdl_renderer_backend.core import preprocess, parse_entity
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core import preprocess, parse_entity

DIR = Path(__file__).resolve().parent / "test_data" / "vhdl_project"


def main() -> int:
    if not DIR.exists():
        print(f"디렉터리 없음: {DIR}", file=sys.stderr)
        return 1
    vhd_files = sorted(DIR.glob("*.vhd"))
    if not vhd_files:
        print(".vhd 파일 없음", file=sys.stderr)
        return 1
    failed = []
    for path in vhd_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        cleaned = preprocess(text)
        entity = parse_entity(cleaned)
        if entity is None:
            print(f"  FAIL: {path.name}  (entity 없음)")
            failed.append(path.name)
            continue
        n = len(entity.ports)
        print(f"  OK:   {path.name:25}  entity={entity.module_name:20}  ports={n}")
    if failed:
        print(f"\n실패: {len(failed)}개 - {failed}", file=sys.stderr)
        return 1
    print(f"\n전체 {len(vhd_files)}개 파일 파싱 성공.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
