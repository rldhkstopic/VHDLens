-- 마이크로 테스트: process + 감지 목록 + 동작 흐름 (if/else, 클럭 동기)
entity REG is
  port (
    CLK : in  std_logic;
    RST : in  std_logic;
    D   : in  std_logic_vector(7 downto 0);
    Q   : out std_logic_vector(7 downto 0)
  );
end entity REG;

architecture rtl of REG is
  signal q_reg : std_logic_vector(7 downto 0);
begin
  process (CLK, RST) is
  begin
    if RST = '1' then
      q_reg <= (others => '0');
    elsif rising_edge(CLK) then
      q_reg <= D;
    end if;
  end process;
  Q <= q_reg;
end architecture rtl;
