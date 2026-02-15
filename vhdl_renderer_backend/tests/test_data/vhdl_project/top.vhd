--------------------------------------------------------------------------------
-- 탑레벨: UART(RS232), 메모리 인터페이스, LED, SPI, 버스 중재, FIFO 연동
-- 파서/시각화 테스트용 복합 프로젝트
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top is
  port (
    -- 클럭/리셋
    CLK_50      : in  std_logic;
    RST_N       : in  std_logic;
    -- RS232
    UART_TX     : out std_logic;
    UART_RX     : in  std_logic;
    -- 메모리 버스 (외부 DRAM/SRAM 등)
    MEM_ADDR    : out std_logic_vector(31 downto 0);
    MEM_DQ      : inout std_logic_vector(31 downto 0);
    MEM_WE_N    : out std_logic;
    MEM_OE_N    : out std_logic;
    MEM_CS_N    : out std_logic;
    MEM_WAIT    : in  std_logic;
    -- LED
    LED         : out std_logic_vector(15 downto 0);
    -- SPI (플래시/센서 등)
    SPI_MOSI    : out std_logic;
    SPI_MISO    : in  std_logic;
    SPI_SCLK    : out std_logic;
    SPI_CS_N    : out std_logic_vector(2 downto 0);
    -- 디버그
    DBG_GPIO    : inout std_logic_vector(7 downto 0)
  );
end entity top;

architecture rtl of top is
  -- 내부 리셋
  signal rst_sync   : std_logic;
  signal uart_tx_s   : std_logic;
  signal uart_rx_s   : std_logic;

  -- UART ↔ 내부 데이터
  signal uart_data_to_tx   : std_logic_vector(7 downto 0);
  signal uart_data_from_rx : std_logic_vector(7 downto 0);
  signal uart_tx_wr       : std_logic;
  signal uart_rx_rd        : std_logic;
  signal uart_tx_ready     : std_logic;
  signal uart_rx_valid     : std_logic;
  signal uart_baud_div     : std_logic_vector(15 downto 0);

  -- 메모리 인터페이스 내부 버스
  signal mem_bus_addr     : std_logic_vector(31 downto 0);
  signal mem_bus_wdata    : std_logic_vector(31 downto 0);
  signal mem_bus_rdata    : std_logic_vector(31 downto 0);
  signal mem_bus_rd       : std_logic;
  signal mem_bus_wr       : std_logic;
  signal mem_bus_ack      : std_logic;
  signal mem_bus_err      : std_logic;
  signal mem_byte_en      : std_logic_vector(3 downto 0);
  signal mem_ready        : std_logic;

  -- LED 제어
  signal led_data         : std_logic_vector(15 downto 0);
  signal led_wr           : std_logic;
  signal led_addr         : std_logic_vector(1 downto 0);
  signal pwm_en           : std_logic;
  signal pwm_duty         : std_logic_vector(7 downto 0);

  -- SPI
  signal spi_tx_data      : std_logic_vector(15 downto 0);
  signal spi_rx_data      : std_logic_vector(15 downto 0);
  signal spi_tx_stb        : std_logic;
  signal spi_rx_valid      : std_logic;
  signal spi_busy          : std_logic;
  signal spi_cpol          : std_logic;
  signal spi_cpha          : std_logic;
  signal spi_width         : std_logic;

  -- 버스 중재
  signal arb_req           : std_logic_vector(3 downto 0);
  signal arb_gnt           : std_logic_vector(3 downto 0);
  signal arb_lock          : std_logic_vector(3 downto 0);
  signal arb_prio          : std_logic_vector(7 downto 0);

  -- FIFO (UART RX → 내부)
  signal fifo_wr_en        : std_logic;
  signal fifo_rd_en        : std_logic;
  signal fifo_din          : std_logic_vector(7 downto 0);
  signal fifo_dout         : std_logic_vector(7 downto 0);
  signal fifo_full         : std_logic;
  signal fifo_empty        : std_logic;
  signal fifo_count        : std_logic_vector(4 downto 0);

  component uart_rs232 is
    port (
      CLK         : in  std_logic;
      RST         : in  std_logic;
      TX          : out std_logic;
      RX          : in  std_logic;
      DATA_IN     : in  std_logic_vector(7 downto 0);
      DATA_OUT    : out std_logic_vector(7 downto 0);
      WR_EN       : in  std_logic;
      RD_EN       : in  std_logic;
      TX_READY    : out std_logic;
      RX_VALID    : out std_logic;
      BAUD_DIV    : in  std_logic_vector(15 downto 0);
      PARITY_EN   : in  std_logic;
      STOP_BITS   : in  std_logic
    );
  end component;

  component memory_interface is
    port (
      CLK           : in  std_logic;
      RST           : in  std_logic;
      ADDR          : out std_logic_vector(31 downto 0);
      DATA_TO_MEM   : out std_logic_vector(31 downto 0);
      DATA_FROM_MEM : in  std_logic_vector(31 downto 0);
      RD_REQ        : out std_logic;
      WR_REQ        : out std_logic;
      BYTE_EN       : out std_logic_vector(3 downto 0);
      MEM_READY     : in  std_logic;
      MEM_WAIT      : in  std_logic;
      BUS_ADDR      : in  std_logic_vector(31 downto 0);
      BUS_WDATA     : in  std_logic_vector(31 downto 0);
      BUS_RDATA     : out std_logic_vector(31 downto 0);
      BUS_RD        : in  std_logic;
      BUS_WR        : in  std_logic;
      BUS_ACK       : out std_logic;
      BUS_ERR       : out std_logic
    );
  end component;

  component led_controller is
    port (
      CLK       : in  std_logic;
      RST       : in  std_logic;
      LED_OUT   : out std_logic_vector(15 downto 0);
      LED_WR    : in  std_logic;
      LED_DATA  : in  std_logic_vector(15 downto 0);
      LED_ADDR  : in  std_logic_vector(1 downto 0);
      PWM_EN    : in  std_logic;
      PWM_DUTY  : in  std_logic_vector(7 downto 0)
    );
  end component;

  component spi_master is
    port (
      CLK       : in  std_logic;
      RST       : in  std_logic;
      MOSI      : out std_logic;
      MISO      : in  std_logic;
      SCLK      : out std_logic;
      CS_N      : out std_logic_vector(2 downto 0);
      TX_DATA   : in  std_logic_vector(15 downto 0);
      RX_DATA   : out std_logic_vector(15 downto 0);
      TX_STB    : in  std_logic;
      RX_VALID  : out std_logic;
      BUSY      : out std_logic;
      CPOL      : in  std_logic;
      CPHA      : in  std_logic;
      WIDTH     : in  std_logic
    );
  end component;

  component bus_arbiter is
    generic ( N_MASTERS : positive := 4 );
    port (
      CLK   : in  std_logic;
      RST   : in  std_logic;
      REQ   : in  std_logic_vector(N_MASTERS - 1 downto 0);
      GNT   : out std_logic_vector(N_MASTERS - 1 downto 0);
      LOCK  : in  std_logic_vector(N_MASTERS - 1 downto 0);
      PRIO  : in  std_logic_vector(N_MASTERS * 2 - 1 downto 0)
    );
  end component;

  component fifo_sync is
    generic (
      DATA_WIDTH : positive := 8;
      DEPTH_LOG2  : positive := 4
    );
    port (
      CLK          : in  std_logic;
      RST          : in  std_logic;
      WR_EN        : in  std_logic;
      RD_EN        : in  std_logic;
      DATA_IN      : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
      DATA_OUT     : out std_logic_vector(DATA_WIDTH - 1 downto 0);
      FULL         : out std_logic;
      EMPTY        : out std_logic;
      ALMOST_FULL  : out std_logic;
      ALMOST_EMPTY : out std_logic;
      COUNT        : out std_logic_vector(DEPTH_LOG2 downto 0)
    );
  end component;

begin
  rst_sync <= not RST_N;

  -- UART 인스턴스
  u_uart : uart_rs232
    port map (
      CLK       => CLK_50,
      RST       => rst_sync,
      TX        => uart_tx_s,
      RX        => uart_rx_s,
      DATA_IN   => uart_data_to_tx,
      DATA_OUT  => uart_data_from_rx,
      WR_EN     => uart_tx_wr,
      RD_EN     => uart_rx_rd,
      TX_READY  => uart_tx_ready,
      RX_VALID  => uart_rx_valid,
      BAUD_DIV  => uart_baud_div,
      PARITY_EN => '0',
      STOP_BITS => '0'
    );
  UART_TX <= uart_tx_s;
  uart_rx_s <= UART_RX;

  -- 메모리 인터페이스
  u_mem : memory_interface
    port map (
      CLK           => CLK_50,
      RST           => rst_sync,
      ADDR          => MEM_ADDR,
      DATA_TO_MEM   => MEM_DQ,
      DATA_FROM_MEM => MEM_DQ,
      RD_REQ        => MEM_OE_N,
      WR_REQ        => MEM_WE_N,
      BYTE_EN       => mem_byte_en,
      MEM_READY     => mem_ready,
      MEM_WAIT      => MEM_WAIT,
      BUS_ADDR      => mem_bus_addr,
      BUS_WDATA     => mem_bus_wdata,
      BUS_RDATA     => mem_bus_rdata,
      BUS_RD        => mem_bus_rd,
      BUS_WR        => mem_bus_wr,
      BUS_ACK       => mem_bus_ack,
      BUS_ERR       => mem_bus_err
    );
  MEM_CS_N <= '0';
  mem_ready <= not MEM_WAIT;

  -- LED 제어기
  u_led : led_controller
    port map (
      CLK     => CLK_50,
      RST     => rst_sync,
      LED_OUT => LED,
      LED_WR  => led_wr,
      LED_DATA=> led_data,
      LED_ADDR=> led_addr,
      PWM_EN  => pwm_en,
      PWM_DUTY=> pwm_duty
    );

  -- SPI 마스터
  u_spi : spi_master
    port map (
      CLK     => CLK_50,
      RST     => rst_sync,
      MOSI    => SPI_MOSI,
      MISO    => SPI_MISO,
      SCLK    => SPI_SCLK,
      CS_N    => SPI_CS_N,
      TX_DATA => spi_tx_data,
      RX_DATA => spi_rx_data,
      TX_STB  => spi_tx_stb,
      RX_VALID=> spi_rx_valid,
      BUSY    => spi_busy,
      CPOL    => spi_cpol,
      CPHA    => spi_cpha,
      WIDTH   => spi_width
    );

  -- 버스 중재기
  u_arb : bus_arbiter
    generic map ( N_MASTERS => 4 )
    port map (
      CLK  => CLK_50,
      RST  => rst_sync,
      REQ  => arb_req,
      GNT  => arb_gnt,
      LOCK => arb_lock,
      PRIO => arb_prio
    );

  -- UART RX → FIFO
  u_fifo : fifo_sync
    generic map ( DATA_WIDTH => 8, DEPTH_LOG2 => 4 )
    port map (
      CLK          => CLK_50,
      RST          => rst_sync,
      WR_EN        => fifo_wr_en,
      RD_EN        => fifo_rd_en,
      DATA_IN      => fifo_din,
      DATA_OUT     => fifo_dout,
      FULL         => fifo_full,
      EMPTY        => fifo_empty,
      ALMOST_FULL  => open,
      ALMOST_EMPTY => open,
      COUNT        => fifo_count
    );
  fifo_wr_en <= uart_rx_valid;
  fifo_din   <= uart_data_from_rx;

  -- 미사용 출력 기본값
  uart_baud_div <= x"028B";
  arb_req <= (others => '0');
  arb_lock <= (others => '0');
  arb_prio <= (others => '0');
  DBG_GPIO <= (others => 'Z');
end architecture rtl;
