--------------------------------------------------------------------------------
-- 메모리 인터페이스
-- 주소/데이터 버스, 읽기·쓰기, 바이트 엔에이블, 대기
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity memory_interface is
  port (
    CLK           : in  std_logic;
    RST           : in  std_logic;
    -- 메모리 버스
    ADDR          : out std_logic_vector(31 downto 0);
    DATA_TO_MEM   : out std_logic_vector(31 downto 0);
    DATA_FROM_MEM : in  std_logic_vector(31 downto 0);
    RD_REQ        : out std_logic;
    WR_REQ        : out std_logic;
    BYTE_EN       : out std_logic_vector(3 downto 0);
    MEM_READY     : in  std_logic;
    MEM_WAIT      : in  std_logic;
    -- 내부 버스 (컨트롤러 접근)
    BUS_ADDR      : in  std_logic_vector(31 downto 0);
    BUS_WDATA     : in  std_logic_vector(31 downto 0);
    BUS_RDATA     : out std_logic_vector(31 downto 0);
    BUS_RD        : in  std_logic;
    BUS_WR        : in  std_logic;
    BUS_ACK       : out std_logic;
    BUS_ERR       : out std_logic
  );
end entity memory_interface;

architecture rtl of memory_interface is
  signal state     : std_logic_vector(1 downto 0);
  signal latched   : std_logic_vector(31 downto 0);
begin
  ADDR <= BUS_ADDR;
  DATA_TO_MEM <= BUS_WDATA;
  BUS_RDATA <= DATA_FROM_MEM;
  BUS_ACK <= MEM_READY;
  BUS_ERR <= '0';
  RD_REQ <= BUS_RD;
  WR_REQ <= BUS_WR;
  BYTE_EN <= (others => '1');
end architecture rtl;
