-- 마이크로 테스트: process + FSM (상태 타입, case/when 동작 흐름)
entity FSM is
  port (
    CLK   : in  std_logic;
    RST   : in  std_logic;
    START : in  std_logic;
    DONE  : out std_logic
  );
end entity FSM;

architecture rtl of FSM is
  type state_t is (IDLE, RUN, DONE_S);
  signal state : state_t;
begin
  process (CLK, RST) is
  begin
    if RST = '1' then
      state <= IDLE;
      DONE  <= '0';
    elsif rising_edge(CLK) then
      case state is
        when IDLE =>
          DONE <= '0';
          if START = '1' then
            state <= RUN;
          end if;
        when RUN =>
          state <= DONE_S;
        when DONE_S =>
          DONE <= '1';
          state <= IDLE;
      end case;
    end if;
  end process;
end architecture rtl;
