# Changelog (VHDLens)

앞으로 수정사항은 아래 형식으로 커밋 메시지와 함께 버전별로 기록합니다.

---

## [초기 기록] — 현재까지 단계 요약

### 기획·설계
- **docs/** 기획·설계 문서 작성
  - 00: 목차, 01: PSD(프로그램 구조도), 02: PRD(요구사항), 03: 기능 상세 명세, 04: VHDL 파싱 전략·검증
  - 4단계 AST 파싱(Black-box → Declaration → Concurrent → Sequential), Tree-sitter 엔진·REQ-09(점진적 파싱/WASM 대비) 반영

### 백엔드 구현
- **전처리기** (`core/preprocessor.py`): 주석 제거, 공백 정규화(선택), 문자열 리터럴 내 `--` 고려
- **Entity 파서** (`core/entity_parser.py`): entity 이름, port(방향/타입/폭), std_logic_vector(N downto M) 지원
- **AST 파서** (`core/ast_parser.py`): Tree-sitter 기반 전체 AST 구축, JSON 덤프, Entity/Port 세분화 추출
- **데이터 모델** (`models/vhdl_types.py`): Port, Entity
- **JSON Exporter** (`exporters/json_exporter.py`): Entity → output.json
- **arch_parser, graph_model, dot_exporter**: 스켈레톤

### 테스트·샘플
- **테스트**: pytest 16개 (전처리기, Entity, AST, 마이크로)
- **test_data/micro**: entity, std_logic_vector, signal, **process**(감지 목록, if/elsif), **process_fsm**(case/when)
- **test_data/vhdl_project**: top, uart_rs232, memory_interface, led_controller, spi_master, bus_arbiter, fifo_sync

### 원격
- **origin**: https://github.com/rldhkstopic/VHDLens.git

---

## [보완] README, requirements, CI

- **README.md (루트):** 프로젝트 소개, 클론/설치/실행/테스트 방법, docs 링크, 브랜치 전략 권장
- **requirements.txt:** pytest, tree-sitter, tree-sitter-vhdl 버전 고정 (pip 설치 재현용)
- **.github/workflows/python-test.yml:** push/PR 시 pytest 자동 실행 (Python 3.10, 3.11)
- **.gitignore:** `.vscode/` 이미 포함됨 (에디터 설정 제외)

---

## 커밋 메시지 규칙 (앞으로)

- `docs: ...` — 문서 수정
- `feat: ...` — 새 기능
- `fix: ...` — 버그 수정
- `test: ...` — 테스트 추가/수정
- `chore: ...` — 빌드/설정/정리
