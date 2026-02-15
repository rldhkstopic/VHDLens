# 파싱 검증 방법

## 1. 자동 테스트 (pytest)

프로젝트 루트에서:

```bash
pip install pytest
python -m pytest vhdl_renderer_backend/tests/test_parsers.py -v
```

**전체 테스트 (Entity + AST):**

```bash
pip install -r requirements.txt
python -m pytest vhdl_renderer_backend/tests/ -v
```

**기대 결과:** 16 passed (Entity 5 + AST 11)

| 구분 | 테스트 | 검증 내용 |
|------|--------|-----------|
| Entity | test_preprocess_* / test_parse_entity_* | 주석 제거, AND_GATE/REGISTER_8BIT/top 포트 |
| AST | test_ast_* | design_file, entity_declaration, AST JSON 직렬화, Entity 추출 |
| 마이크로 | test_micro_entity_port / test_std_logic_vector / test_signal | entity, vector(7 downto 0), architecture, signal |
| **동작 흐름** | **test_micro_process_ast_has_process_and_flow** | **process, 감지 목록, if/elsif, rising_edge(CLK), sequential_block** |
| **동작 흐름** | **test_micro_process_fsm_ast_has_case_flow** | **process, sensitivity_list, case/when FSM** |

---

## 2. CLI로 개별 파일 파싱

```bash
# 탑레벨 (복합 프로젝트)
python -m vhdl_renderer_backend.main vhdl_renderer_backend/tests/test_data/vhdl_project/top.vhd -o top_out.json

# UART 엔티티
python -m vhdl_renderer_backend.main vhdl_renderer_backend/tests/test_data/vhdl_project/uart_rs232.vhd -o uart_out.json

# 메모리 인터페이스
python -m vhdl_renderer_backend.main vhdl_renderer_backend/tests/test_data/vhdl_project/memory_interface.vhd -o mem_out.json
```

생성된 JSON에서 `module_name`, `ports[]`(name, direction, type, width) 확인.

---

## 3. vhdl_project 전체 엔티티 한 번에 확인

각 .vhd에서 첫 번째 entity만 파싱됩니다. 프로젝트 내 모든 엔티티를 검증하려면:

```bash
for f in vhdl_renderer_backend/tests/test_data/vhdl_project/*.vhd; do
  python -m vhdl_renderer_backend.main "$f" -o "out_$(basename $f .vhd).json"
done
```

(Windows PowerShell에서는 Get-ChildItem + ForEach-Object로 동일하게 실행 가능)
