-- 마이크로 테스트: architecture + signal 선언
entity DFF is
  port ( CLK : in std_logic; D : in std_logic; Q : out std_logic );
end entity DFF;

architecture rtl of DFF is
  signal q_internal : std_logic;
begin
  Q <= q_internal;
end architecture rtl;
