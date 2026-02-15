# VHDL 세부 문법 파싱 전략 및 검증

**목적:** 단순 포트/컴포넌트를 넘어, 타입·선언·병행/순차 구문까지 **누락 없이** 파싱·세분화하기 위한 4단계 전략과 검증 방법 정리.

---

## 1. 4단계 파싱 (Phased Approach)

| 단계 | 수준 | 파싱 대상 | 세분화 포인트 |
|------|------|-----------|----------------|
| **1단계** | Black-box | `library`, `use`, `entity`, `port`, `generic` | Port: 방향, 타입(`std_logic`/`std_logic_vector`/`unsigned`), 버스 폭 `(7 downto 0)`, 초기값 |
| **2단계** | Declaration | architecture 선언부: `signal`, `constant`, `variable`, 사용자 정의 `type` | `type ... is array`, `type ... is record`, enum/상태 타입(FSM) → 개별 노드 |
| **3단계** | Concurrent & Structural | `component` 인스턴스(`port map`/`generic map`), `<=`, `when...else`, `with...select`, `for/if generate` | generate 반복 블록 구조화 |
| **4단계** | Sequential & Behavioral | `process`, 감지 목록, `if/elsif/else`, `case/when`, `for/while` | `rising_edge(clk)` 등 조건, FSM 상태 전이 데이터 |

---

## 2. 검증 전략

### 2.1 AST 노드 덤프 (JSON Full Dump)

- 파서가 읽은 **전체 트리**를 JSON으로 출력.
- `Unknown` 또는 통째로 스킵된 블록이 있는지 눈으로 확인.
- 옵션: `output_ast_tree.json` 등으로 저장.

### 2.2 문법별 마이크로 테스트 (Micro Test-suite)

- 한 파일에 **해당 문법 하나만** 포함한 소형 VHDL 파일 다수 유지.
- 예: `test_array_type.vhd`, `test_generate_statement.vhd`, `test_process_fsm.vhd`, `test_port_map.vhd`.
- 테스트 스크립트가 각 파일을 파싱해 "해당 문법이 정확한 JSON 계층으로 분리되었는지" 자동 검증.

### 2.3 파서 엔진 권장

- **정규표현식만**으로 위 수준의 파싱은 엣지 케이스 때문에 한계가 있음.
- **Tree-sitter** (VHDL grammar) 또는 **ANTLR4** (VHDL grammar) 등으로 파서 생성 권장.
- Tree-sitter: 에디터용 실시간·점진적 파싱, WASM 경량화에 유리.

---

## 3. VS Code 확장 '무게' 대응 (REQ-09)

- **Tree-sitter:** C 기반, WASM으로 수백 KB 수준. **점진적 파싱**으로 수정 구간만 갱신 → 타이핑 시 렉 최소화.
- Python 바인딩으로 현재 파이프라인 유지, 추후 TypeScript/WASM 전환 시 렌더링 로직 구조 재사용.

이 문서는 [02-요구사항_정의서_PRD.md](02-요구사항_정의서_PRD.md), [03-기능_상세_명세서.md](03-기능_상세_명세서.md)와 함께 참고합니다.
