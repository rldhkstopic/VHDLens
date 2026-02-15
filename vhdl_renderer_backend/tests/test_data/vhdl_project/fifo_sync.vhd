--------------------------------------------------------------------------------
-- 동기 FIFO (UART ↔ 내부 데이터 경로 버퍼)
-- 깊이 16, 8비트 데이터, almost full/empty
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity fifo_sync is
  generic (
    DATA_WIDTH : positive := 8;
    DEPTH_LOG2  : positive := 4
  );
  port (
    CLK         : in  std_logic;
    RST         : in  std_logic;
    WR_EN       : in  std_logic;
    RD_EN       : in  std_logic;
    DATA_IN     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
    DATA_OUT    : out std_logic_vector(DATA_WIDTH - 1 downto 0);
    FULL        : out std_logic;
    EMPTY       : out std_logic;
    ALMOST_FULL : out std_logic;
    ALMOST_EMPTY: out std_logic;
    COUNT       : out std_logic_vector(DEPTH_LOG2 downto 0)
  );
end entity fifo_sync;

architecture rtl of fifo_sync is
  type mem_t is array (0 to 2**DEPTH_LOG2 - 1) of std_logic_vector(DATA_WIDTH - 1 downto 0);
  signal mem    : mem_t;
  signal wptr   : unsigned(DEPTH_LOG2 downto 0);
  signal rptr   : unsigned(DEPTH_LOG2 downto 0);
  signal count_i: unsigned(DEPTH_LOG2 downto 0);
begin
  COUNT <= std_logic_vector(count_i);
  FULL <= '0';
  EMPTY <= '1';
  ALMOST_FULL <= '0';
  ALMOST_EMPTY <= '1';
  DATA_OUT <= (others => '0');
end architecture rtl;
