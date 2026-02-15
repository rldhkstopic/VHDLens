--------------------------------------------------------------------------------
-- RS232 / UART 인터페이스
-- 보드레이트 설정, TX/RX, 8비트 데이터, valid/ready 핸드셰이크
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;

entity uart_rs232 is
  port (
    CLK         : in  std_logic;
    RST         : in  std_logic;
    -- 직렬 입출력
    TX          : out std_logic;
    RX          : in  std_logic;
    -- 병렬 데이터 (호스트 측)
    DATA_IN     : in  std_logic_vector(7 downto 0);
    DATA_OUT    : out std_logic_vector(7 downto 0);
    WR_EN       : in  std_logic;
    RD_EN       : in  std_logic;
    TX_READY    : out std_logic;
    RX_VALID    : out std_logic;
    -- 보드레이트 설정 (클럭 분주비)
    BAUD_DIV    : in  std_logic_vector(15 downto 0);
    PARITY_EN   : in  std_logic;
    STOP_BITS   : in  std_logic  -- 0: 1 stop, 1: 2 stop
  );
end entity uart_rs232;

architecture rtl of uart_rs232 is
  signal baud_tick   : std_logic;
  signal tx_state    : std_logic_vector(2 downto 0);
  signal rx_state    : std_logic_vector(2 downto 0);
  signal shift_tx    : std_logic_vector(9 downto 0);
  signal shift_rx    : std_logic_vector(9 downto 0);
  signal bit_cnt_tx  : integer range 0 to 15;
  signal bit_cnt_rx  : integer range 0 to 15;
begin
  -- (동작 로직 생략: 파서 테스트용 구조만)
  TX <= '1';
  DATA_OUT <= (others => '0');
  TX_READY <= '1';
  RX_VALID <= '0';
end architecture rtl;
