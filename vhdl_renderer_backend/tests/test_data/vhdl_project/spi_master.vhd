--------------------------------------------------------------------------------
-- SPI 마스터
-- MOSI, MISO, SCLK, CS, 8/16비트 전송, CPOL/CPHA
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;

entity spi_master is
  port (
    CLK       : in  std_logic;
    RST       : in  std_logic;
    -- SPI 신호
    MOSI      : out std_logic;
    MISO      : in  std_logic;
    SCLK      : out std_logic;
    CS_N      : out std_logic_vector(2 downto 0);  -- 슬레이브 선택
    -- 데이터
    TX_DATA   : in  std_logic_vector(15 downto 0);
    RX_DATA   : out std_logic_vector(15 downto 0);
    TX_STB    : in  std_logic;
    RX_VALID  : out std_logic;
    BUSY      : out std_logic;
    -- 모드
    CPOL      : in  std_logic;
    CPHA      : in  std_logic;
    WIDTH     : in  std_logic  -- 0: 8bit, 1: 16bit
  );
end entity spi_master;

architecture rtl of spi_master is
  signal shift_tx   : std_logic_vector(15 downto 0);
  signal shift_rx   : std_logic_vector(15 downto 0);
  signal bit_cnt    : integer range 0 to 15;
  signal sclk_internal : std_logic;
begin
  SCLK <= sclk_internal;
  MOSI <= shift_tx(15);
  RX_DATA <= shift_rx;
  RX_VALID <= '0';
  BUSY <= '0';
  CS_N <= (others => '1');
end architecture rtl;
