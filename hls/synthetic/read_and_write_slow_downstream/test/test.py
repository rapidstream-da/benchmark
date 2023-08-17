"""Read and write downstream cocotb testbench."""

import subprocess
import glob
import logging

import cocotb

from cocotb.handle import HierarchyObject
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
from cocotbext.axi import AxiBus, AxiLiteMaster, AxiRam, AxiLiteBus
from cocotb_test.simulator import run

from utils import add_space_before_comments

_logger = logging.getLogger(__name__)
DATA_LEN = 32  # input & output array length

@cocotb.test()
async def test(dut: HierarchyObject, deley_count: int = 200) -> None:
    """Main testbench."""
    CLK = Clock(dut.ap_clk, 3.33, units="ns")

    # start clock
    cocotb.start_soon(CLK.start(start_high=False))

    # init interface
    # clock = ap_clk, reset = ap_rst_n, active low reset
    ctrl = AxiLiteMaster(
        AxiLiteBus.from_prefix(dut, "s_axi_control"), dut.ap_clk, dut.ap_rst_n,
        reset_active_level=False
    )

    # clock = ap_clk, reset = ap_rst_n, active low reset, size = 128 bytes
    # (4 bytes per int times 32 numbers)
    gmem_A = AxiRam(
        AxiBus.from_prefix(dut, "m_axi_gmem_A"), dut.ap_clk, dut.ap_rst_n,
        reset_active_level=False, size=4*32
    )

    # clock = ap_clk, reset = ap_rst_n, active low reset, size = 128 bytes
    # (4 bytes per int times 32 numbers)
    gmem_B = AxiRam(
        AxiBus.from_prefix(dut, "m_axi_gmem_B"), dut.ap_clk, dut.ap_rst_n,
        reset_active_level=False, size=4*32
    )

    # init memory
    for i in range(DATA_LEN):
        gmem_A.write(i*4, i.to_bytes(4, 'little'))
    for i in range(DATA_LEN):
        gmem_B.write(i*4, b'\x00\x00\x00\x00')

    for i in range(DATA_LEN):
        read_value = gmem_B.read_word(i*4, ws=4)
        assert read_value == 0

    # reset 5 cycles
    dut.ap_rst_n.value = 0
    for _i in range(10):
        await RisingEdge(dut.ap_clk)
    dut.ap_rst_n.value = 1
    await RisingEdge(dut.ap_clk)

    # init control registers
    await ctrl.write(0x00, b'\x00')  # ap_ctrl registers
    await RisingEdge(dut.ap_clk)
    await ctrl.write(0x10, b'\x00')  # mem_0 registers
    await RisingEdge(dut.ap_clk)
    await ctrl.write(0x18, b'\x00')  # mem_1 registers
    await RisingEdge(dut.ap_clk)

    # set ap_start
    await ctrl.write(0x00, b'\x01')
    await RisingEdge(dut.ap_clk)

    # wait until ap_done is set or timeout
    ap_done = 0
    count = deley_count
    while ap_done == 0:
        byte = await ctrl.read_byte(0x00)
        ap_done = byte // 2 % 2  # get bit[1](ap_done) of byte
        count -= 1
        if count == 0:
            raise TimeoutError("Timeout before ap_done is set")

    for i in range(DATA_LEN):
        read_value = gmem_B.read_word(i*4, ws=4)
        assert i == read_value


def main():
    """Synthesis HLS and run cocotb testbench."""
    logging.basicConfig(level=logging.INFO)

    _logger.info("Running HLS synthesis...")
    gen_hls = subprocess.run(
        ["vitis_hls", "-f", "./generate_rtl.tcl"],
        check=False,
        capture_output=True
    )

    if gen_hls.returncode != 0:
        raise RuntimeError(gen_hls.stdout.decode("utf-8"))
    _logger.info("HLS synthesis complete")

    _logger.info("Preparing testbench...")
    source_paths = glob.glob("**/syn/verilog/*.v", recursive=True)

    # hack: add a space before comment to avoid error.
    # HLS generates line in forms of "default_nettype wire//*".
    # Iverilog recognizes wire and //* as a whole and throw an error.
    add_space_before_comments(source_paths)

    _logger.info("Running test...")
    run(
        verilog_sources=source_paths,  # sources
        toplevel="top",  # top level HDL
        module="test"  # name of cocotb test module
    )
    _logger.info("Test finished")


if __name__ == "__main__":
    main()
