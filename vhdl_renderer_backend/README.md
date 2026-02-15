# VHDL Renderer Backend

VHDL 파싱 및 시각적 디버깅용 백엔드. 웹 테스터·VS Code 확장 연동을 위한 Entity/Port 추출, **Tree-sitter AST** 기반 세부 파싱 및 JSON 출력.

## 설치

```bash
pip install -r requirements.txt
# requirements: pytest, tree-sitter>=0.25, tree-sitter-vhdl>=1.2
```

## 디렉터리 구조

```
vhdl_renderer_backend/
├── main.py              # CLI 진입점
├── core/
│   ├── preprocessor.py  # 주석 제거, 공백 정규화
│   ├── ast_parser.py    # Tree-sitter AST 파서 (덤프, Entity/Port 추출)
│   ├── entity_parser.py # Entity+Port 추출 (1단계 호환)
│   └── arch_parser.py   # (스켈레톤) Architecture/Signal/Component
├── models/
│   ├── vhdl_types.py    # Port, Entity 데이터 클래스
│   └── graph_model.py   # (스켈레톤) 그래프 모델
├── exporters/
│   ├── json_exporter.py # JSON 저장
│   └── dot_exporter.py  # (스켈레톤) Graphviz
└── tests/
    ├── test_data/       # 샘플 .vhd
    │   ├── and_gate.vhd, register_8bit.vhd
    │   ├── vhdl_project/   # 복합 테스트 프로젝트
    │   └── micro/          # 문법별 마이크로 테스트 (entity, signal, vector, process, FSM)
    ├── test_parsers.py  # pytest (전처리기, Entity)
    ├── test_ast_parser.py  # pytest (AST 파서)
    └── run_ast_dump.py  # AST 전체 JSON 덤프 스크립트
```

## 실행 방법

**프로젝트 루트(vhdl_Viz)에서:**

```bash
# JSON 출력 (기본: 입력과 같은 폴더에 output.json)
python -m vhdl_renderer_backend.main path/to/file.vhd

# 출력 경로 지정
python -m vhdl_renderer_backend.main path/to/file.vhd -o out.json

# 공백 정규화 없이 주석만 제거
python -m vhdl_renderer_backend.main path/to/file.vhd --no-normalize

# 복합 테스트 프로젝트 탑레벨 파싱
python -m vhdl_renderer_backend.main vhdl_renderer_backend/tests/test_data/vhdl_project/top.vhd -o vhdl_project_output.json
```

**backend 폴더에서:**

```bash
cd vhdl_renderer_backend
python main.py ../tests/test_data/and_gate.vhd -o output.json
```

## 테스트

```bash
pip install -r requirements.txt
python -m pytest vhdl_renderer_backend/tests/ -v
```

**세부 파싱 검증:** AST 테스트 11개 + Entity 5개 = 16개 통과. 마이크로 테스트에 **process + 감지 목록 + if/elsif + case/when(FSM)** 동작 흐름 포함 (`test_process.vhd`, `test_process_fsm.vhd`).

## AST 전체 덤프 (Full Dump)

```bash
python vhdl_renderer_backend/tests/run_ast_dump.py path/to/file.vhd output_ast_tree.json
```

생성된 JSON에서 `design_file` → `design_unit` → `entity_declaration`, `library_clause`, `line_comment` 등 모든 노드가 세분화되어 있는지 확인 가능.

## 구현 상태

- **전처리기**: `--` 주석 제거, 선택적 공백 정규화 (문자열 리터럴 내 `--` 고려)
- **AST 파서 (Tree-sitter)**: 전체 AST 구축, JSON 덤프, Entity/Port 세분화 추출 (interface_declaration, mode, subtype_indication)
- **Entity 파서 (레거시)**: `entity NAME is`, `port ( ... );` 정규식 파싱
- **JSON Exporter**: Entity → `output.json`
- **Architecture 파서 / Dot Exporter**: 스켈레톤만 있음
