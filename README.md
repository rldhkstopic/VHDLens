# VHDLens

**Tree-sitter 기반 VHDL 실시간 렌더링 파서** — VHDL 소스를 파싱하여 Entity/Port, Signal, Process 등으로 세분화하고, JSON·Graphviz로 출력합니다. 웹 테스터 및 VS Code 확장 프로그램 연동을 목표로 합니다.

---

## 빠른 시작

### 1. 저장소 클론 및 의존성 설치

```bash
git clone https://github.com/rldhkstopic/VHDLens.git
cd VHDLens
pip install -r requirements.txt
```

### 2. 로컬 실행

```bash
# VHDL 파일 파싱 → JSON 출력 (Entity/Port)
python -m vhdl_renderer_backend.main vhdl_renderer_backend/tests/test_data/vhdl_project/top.vhd -o output.json

# AST 전체 덤프 (세부 노드 확인)
python vhdl_renderer_backend/tests/run_ast_dump.py vhdl_renderer_backend/tests/test_data/vhdl_project/top.vhd top_ast.json
```

### 3. 테스트 실행

```bash
python -m pytest vhdl_renderer_backend/tests/ -v
```

**기대 결과:** 16 passed (전처리기, Entity 파서, AST 파서, 마이크로 테스트 포함 process/FSM)

---

## 프로젝트 구조

| 경로 | 설명 |
|------|------|
| **docs/** | 기획·설계 문서 (PSD, PRD, 기능 상세, 4단계 파싱 전략) |
| **vhdl_renderer_backend/** | 파이썬 백엔드 (전처리기, Entity/AST 파서, JSON export) |
| **vhdl_renderer_backend/tests/** | pytest 및 테스트용 VHDL (micro, vhdl_project) |
| **requirements.txt** | Python 의존성 (pytest, tree-sitter, tree-sitter-vhdl) |

- **기획 문서 목차:** [docs/00-기획_설계_목차.md](docs/00-기획_설계_목차.md)  
- **백엔드 상세:** [vhdl_renderer_backend/README.md](vhdl_renderer_backend/README.md)

---

## 주요 기능

- **전처리기:** 주석 제거, 공백 정규화
- **Entity 파서:** entity 이름, port(방향/타입/폭) 추출
- **AST 파서 (Tree-sitter):** 전체 AST 구축, JSON 덤프, Entity/Port 세분화, process/sensitivity/case 등 동작 흐름 노드 인식
- **JSON Exporter:** 파싱 결과 → `output.json` (웹/VS Code 연동용)

---

## 브랜치 전략 (권장)

- **master/main:** 안정 버전
- 기능 개발 시 `feat/기능명` 브랜치에서 작업 후 병합 (예: `feat/ast-process`)

---

## 라이선스 및 기여

저장소는 [rldhkstopic/VHDLens](https://github.com/rldhkstopic/VHDLens)에서 관리됩니다. 변경 이력은 [CHANGELOG.md](CHANGELOG.md)를 참고하세요.
