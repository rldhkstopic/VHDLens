-- 8-bit register with std_logic_vector ports
entity REGISTER_8BIT is
  port (
    CLK   : in  std_logic;
    RST   : in  std_logic;
    D     : in  std_logic_vector(7 downto 0);
    Q     : out std_logic_vector(7 downto 0)
  );
end entity REGISTER_8BIT;
