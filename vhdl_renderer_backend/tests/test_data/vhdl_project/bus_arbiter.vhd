--------------------------------------------------------------------------------
-- 버스 중재기 (멀티 마스터)
-- 요청/승인, 우선순위, 잠금
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;

entity bus_arbiter is
  generic (
    N_MASTERS : positive := 4
  );
  port (
    CLK       : in  std_logic;
    RST       : in  std_logic;
    -- 마스터 요청/승인
    REQ       : in  std_logic_vector(N_MASTERS - 1 downto 0);
    GNT       : out std_logic_vector(N_MASTERS - 1 downto 0);
    LOCK      : in  std_logic_vector(N_MASTERS - 1 downto 0);
    -- 우선순위 (고정 또는 동적)
    PRIO      : in  std_logic_vector(N_MASTERS * 2 - 1 downto 0)
  );
end entity bus_arbiter;

architecture rtl of bus_arbiter is
  signal gnt_internal : std_logic_vector(N_MASTERS - 1 downto 0);
begin
  GNT <= gnt_internal;
  -- (라운드로빈/고정 우선순위 로직 생략)
end architecture rtl;
