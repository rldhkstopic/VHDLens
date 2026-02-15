# 변경 이력 (Changelog)

앞으로 수정사항은 **받은 지시 → 진행한 과정**을 요약해 버전별로 기록합니다.

---

## [0.1.0] - 2025-02-14 (초기 버전)

### 받은 지시 / 목표

- VHDL 파싱 및 시각적 디버깅 1단계: 기획·설계 문서화 후 파서 백엔드 구현
- 최종 목표: VS Code 확장 프로그램. 단계적으로 웹 기반 테스트 후 연동
- 세부 문법까지 AST 기반 파싱, Tree-sitter 도입, 4단계 파싱 전략 반영
- 테스트는 문법별 마이크로 테스트 + process/동작 흐름 포함
- 수정사항은 커밋으로 요약·버전 관리, GitHub에 기록

### 진행한 과정

1. **기획·설계 문서**
   - `docs/00-기획_설계_목차.md` ~ `04-VHDL_파싱_전략_및_검증.md` 작성
   - PSD(프로그램 구조도), PRD(요구사항 정의서), 기능 상세 명세서
   - Flutter/앱 제거 → 웹 테스트 + VS Code 확장 연동으로 정정
   - 4단계 AST 파싱(Black-box → Declaration → Concurrent → Sequential), Tree-sitter·REQ-09(점진적 파싱) 반영

2. **디렉터리·뼈대 및 1단계 파서**
   - `vhdl_renderer_backend/` 구조 생성 (core, models, exporters, tests)
   - 전처리기 `preprocessor.py`: 주석 제거, 공백 정규화 (문자열 내 `--` 고려)
   - `entity_parser.py`: entity 이름, port(방향/타입/폭) 추출, std_logic_vector(N downto M) 지원
   - `models/vhdl_types.py`: Port, Entity 데이터 클래스
   - `exporters/json_exporter.py`: Entity → JSON 저장
   - `main.py`: CLI (파일 로드 → 전처리 → Entity 파싱 → JSON 출력)

3. **테스트용 VHDL 프로젝트**
   - `tests/test_data/vhdl_project/`: top, uart_rs232, memory_interface, led_controller, spi_master, bus_arbiter, fifo_sync
   - 복합 인터페이스(UART, 메모리, LED, SPI) + component/signal/port map

4. **Tree-sitter AST 파서**
   - `tree-sitter`(>=0.25), `tree-sitter-vhdl` 설치 및 `core/ast_parser.py` 구현
   - `parse_to_tree`, `ast_to_dict`, `ast_dump_json`, `extract_entity_ports_from_tree`
   - AST 전체 JSON 덤프로 세부 노드(주석, library, entity, port, subtype_indication 등) 검증

5. **문법별 마이크로 테스트 및 동작 흐름**
   - `test_data/micro/`: test_entity_port, test_std_logic_vector, test_signal, **test_process**, **test_process_fsm**
   - test_process: process(CLK,RST), if/elsif, rising_edge(CLK), sequential_block
   - test_process_fsm: process, sensitivity_list, case/when 상태 전이
   - pytest: test_parsers.py(5) + test_ast_parser.py(11) = 16개 통과

6. **문서·검증**
   - README, run_parsing_check.md, run_ast_dump.py, run_all_vhdl_project.py
   - requirements.txt: pytest, tree-sitter, tree-sitter-vhdl

### 버전 관리 규칙 (앞으로)

- 커밋 메시지: `[버전/영역] 받은 지시 요약 → 진행한 작업 한 줄`
- CHANGELOG.md: 버전별로 "받은 지시" / "진행한 과정" 요약 추가
