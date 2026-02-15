--------------------------------------------------------------------------------
-- LED 제어기
-- 8/16/32 LED 출력, PWM 밝기(선택), 스트로브 입력
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;

entity led_controller is
  port (
    CLK       : in  std_logic;
    RST       : in  std_logic;
    -- LED 출력
    LED_OUT   : out std_logic_vector(15 downto 0);
    -- 제어
    LED_WR    : in  std_logic;
    LED_DATA  : in  std_logic_vector(15 downto 0);
    LED_ADDR  : in  std_logic_vector(1 downto 0);   -- 0: 데이터, 1: 방향, 2: PWM
    PWM_EN    : in  std_logic;
    PWM_DUTY  : in  std_logic_vector(7 downto 0)
  );
end entity led_controller;

architecture rtl of led_controller is
  signal reg_data   : std_logic_vector(15 downto 0);
  signal reg_dir    : std_logic_vector(15 downto 0);
  signal pwm_cnt    : unsigned(7 downto 0);
begin
  LED_OUT <= reg_data when PWM_EN = '0' else
             reg_data when pwm_cnt < unsigned(PWM_DUTY) else (others => '0');
  -- (레지스터/카운터 로직 생략)
end architecture rtl;
