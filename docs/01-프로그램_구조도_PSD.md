# 프로그램 구조도 (PSD: Program Structure Diagram)

**프로젝트:** VHDL 파싱 및 시각적 디버깅  
**목적:** 파이썬 기반 모듈화 아키텍처로, 각 기능이 독립적으로 동작하여 유지보수·테스트 및 향후 **웹 테스터와 VS Code 확장 프로그램(Extension)** 연동이 용이하도록 설계. **AST 기반 4단계 파싱** 및 **Tree-sitter** 엔진 도입으로 세부 문법 전면 커버 및 점진적 파싱(WASM 대비)을 목표로 한다.

---

## 디렉터리 구조

```
vhdl_renderer_backend/
│
├── main.py                 # 프로그램 진입점 (CLI 인터페이스)
│
├── core/                   # 핵심 파싱 로직
│   ├── preprocessor.py     # 주석 제거 및 텍스트 정규화
│   ├── ast_parser.py       # [목표] Tree-sitter 기반 AST 파서 (4단계 통합)
│   ├── entity_parser.py    # Entity 및 Port 추출 (1단계 호환/레거시)
│   └── arch_parser.py      # Architecture, Component, Signal 추출
│
├── models/                 # 내부 데이터 모델 (자료구조)
│   ├── vhdl_types.py       # Port, Signal, Component, ProcessBlock, TypeDef 등
│   └── graph_model.py      # 노드와 간선(Edge)을 관리하는 트리 구조
│
├── exporters/              # 결과물 출력 모듈
│   ├── json_exporter.py    # 프론트엔드 전달용 JSON / AST 전체 덤프
│   └── dot_exporter.py     # 시각적 디버깅용 Graphviz (.dot) 생성
│
└── tests/                  # 단계별 디버깅 및 테스트 환경
    ├── test_data/          # 테스트용 .vhd 샘플 및 문법별 마이크로 테스트
    └── test_parsers.py     # 자동화 테스트 스크립트 (pytest)
```

---

## 모듈 역할 요약

| 경로 | 역할 |
|------|------|
| `main.py` | CLI 진입점, 파일 로드 → 파서 파이프라인 호출 → Export 선택 |
| `core/preprocessor.py` | VHDL 원문 전처리(주석 제거, 정규화) |
| `core/ast_parser.py` | Tree-sitter 기반 AST 구축 및 4단계 세분화 추출 (목표) |
| `core/entity_parser.py` | Entity 이름, Port 목록 추출 (1단계 호환) |
| `core/arch_parser.py` | Architecture 내 Signal, Component, Port Map 추출 |
| `models/vhdl_types.py` | Port, Signal, Component, ProcessBlock, TypeDef 등 도메인 데이터 클래스 |
| `models/graph_model.py` | 노드·엣지 기반 그래프 모델 (시각화/연동용) |
| `exporters/json_exporter.py` | 데이터 모델 → JSON / AST 전체 덤프 (프론트엔드 연동) |
| `exporters/dot_exporter.py` | 데이터 모델 → Graphviz DOT/이미지 (디버깅) |
| `tests/` | pytest 기반 단위/통합 테스트, 문법별 마이크로 테스트 파일 |

---

## 데이터 흐름 (고수준)

```
[.vhd 파일] → main.py
    → preprocessor
    → ast_parser (Tree-sitter)  ← 1~4단계 통합 목표
        또는 entity_parser → arch_parser (1단계 호환)
    → models (vhdl_types + graph_model)
    → json_exporter / dot_exporter
    → [output.json], [output_ast_tree.json], [debug_graph.png 등]
```

이 구조는 **API 형태로 웹 테스터에 연동하거나, 향후 VS Code 확장 프로그램의 백엔드(WASM 점진적 파싱/LSP)로 붙이기 쉽도록** 파서 로직과 데이터 모델을 분리한 설계입니다.
