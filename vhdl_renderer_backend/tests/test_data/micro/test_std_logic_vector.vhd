-- 마이크로 테스트: std_logic_vector 포트
entity REG is
  port (
    CLK : in  std_logic;
    D   : in  std_logic_vector(7 downto 0);
    Q   : out std_logic_vector(7 downto 0)
  );
end entity REG;
