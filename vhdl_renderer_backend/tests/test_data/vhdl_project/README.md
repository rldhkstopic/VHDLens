# VHDL 테스트 프로젝트 (복합 인터페이스)

파서/시각화 테스트용 샘플 프로젝트. 다양한 통신·메모리·LED 인터페이스가 한 탑레벨에서 얽혀 있는 구조.

## 구성

| 파일 | 설명 |
|------|------|
| `top.vhd` | 탑레벨: UART, 메모리, LED, SPI, 내부 버스/Arbiter 인스턴스화 |
| `uart_rs232.vhd` | RS232/UART 송수신 (TX, RX, 보드레이트, 데이터 버스) |
| `memory_interface.vhd` | 메모리 인터페이스 (주소/데이터 버스, 읽기/쓰기, 대기) |
| `led_controller.vhd` | LED 제어 (출력 벡터, 스트로브) |
| `spi_master.vhd` | SPI 마스터 (MOSI, MISO, SCLK, CS) |
| `bus_arbiter.vhd` | 내부 버스 중재 (요청/승인, 멀티 마스터) |
| `fifo_sync.vhd` | 동기 FIFO (UART↔내부 버퍼 연결용) |

## 의존 관계 (대략)

```
top
 ├── uart_rs232
 ├── memory_interface
 ├── led_controller
 ├── spi_master
 ├── bus_arbiter
 └── fifo_sync (UART ↔ 내부 데이터 경로)
```

## 테스트 실행

프로젝트 루트에서:

```bash
python -m vhdl_renderer_backend.main vhdl_renderer_backend/tests/test_data/vhdl_project/top.vhd -o vhdl_project_output.json
```
