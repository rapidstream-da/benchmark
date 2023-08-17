"""Read and write cocotb testbench."""

import subprocess
import glob
import logging
import math

from utils import add_space_before_comments
from floating_point_adder import fadd, float_to_bytes, bytes_to_float

from cocotbext.axi import AxiBus, AxiLiteMaster, AxiRam, AxiLiteBus
from cocotb_test.simulator import run
from cocotb.handle import HierarchyObject
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock

import cocotb


_logger = logging.getLogger(__name__)
DATA_LEN = 32  # input & output array length


class VecaddTest:
    """Vector add testbench class."""

    def __init__(self, dut: HierarchyObject):
        """Initialize testbench."""
        self.dut = dut
        CLK = Clock(dut.ap_clk, 3.33, units="ns")

        # start clocks
        _logger.info("Start clock")
        cocotb.start_soon(CLK.start(start_high=False))

        # init interface
        _logger.info("Initialize interfaces")

        # clock = ap_clk, reset = ap_rst_n, active low reset
        self.ctrl = AxiLiteMaster(
            AxiLiteBus.from_prefix(dut, "s_axi_control"),
            dut.ap_clk,
            dut.ap_rst_n,
            reset_active_level=False,
        )

        # clock = ap_clk, reset = ap_rst_n, active low reset, size = 128 bytes
        # (4 bytes per int times 32 numbers)
        def _gen_ram(prefix: str) -> AxiRam:
            return AxiRam(
                AxiBus.from_prefix(dut, prefix),
                dut.ap_clk,
                dut.ap_rst_n,
                reset_active_level=False,
                size=4 * 32,
            )

        self.gmem_A = _gen_ram("m_axi_gmem_A")
        self.gmem_B = _gen_ram("m_axi_gmem_B")
        self.gmem_C = _gen_ram("m_axi_gmem_C")

        # add floating point ip simulator
        _logger.info("Add floating point ip simulator")
        fadd_ip = dut.compute_U0.fadd_32ns_32ns_32_7_full_dsp_1_U15.\
            top_fadd_32ns_32ns_32_7_full_dsp_1_ip_u
        self.adder = fadd(
            fadd_ip.aclk,
            fadd_ip.aclken,
            fadd_ip.s_axis_a_tvalid,
            fadd_ip.s_axis_a_tdata,
            fadd_ip.s_axis_b_tvalid,
            fadd_ip.s_axis_b_tdata,
            fadd_ip.m_axis_result_tvalid,
            fadd_ip.m_axis_result_tdata,
            5,
        )

    async def reset(self) -> None:
        """Reset testbench."""
        dut = self.dut
        gmem_A, gmem_B, gmem_C = self.gmem_A, self.gmem_B, self.gmem_C
        ctrl = self.ctrl

        # init memory
        _logger.info("Initialize memory")
        for i in range(DATA_LEN):
            bytes_i = float_to_bytes(float(i), "little")
            gmem_A.write(i*4, bytes_i)
            gmem_B.write(i*4, bytes_i)
        for i in range(DATA_LEN):
            gmem_C.write(i*4, b'\x00\x00\x00\x00')

        for i in range(DATA_LEN):
            read_value = gmem_C.read_word(i*4, ws=4)
            assert read_value == 0

        # reset 5 cycles
        _logger.info("Reset signal on")
        dut.ap_rst_n.value = 0
        for _i in range(10):
            await RisingEdge(dut.ap_clk)
        dut.ap_rst_n.value = 1
        await RisingEdge(dut.ap_clk)
        _logger.info("Reset signal off")

        # init control registers
        _logger.info("Initialize control registers")
        for addr, data in (
            (0x00, b'\x00'),              # ap_ctrl registers
            (0x10, b'\x00\x00\x00\x00'),  # mem_0 registers
            (0x14, b'\x00\x00\x00\x00'),  # mem_0 registers
            (0x1c, b'\x00\x00\x00\x00'),  # mem_1 registers
            (0x20, b'\x00\x00\x00\x00'),  # mem_1 registers
            (0x28, b'\x00\x00\x00\x00'),  # mem_2 registers
            (0x2c, b'\x00\x00\x00\x00'),  # mem_2 registers
        ):
            await ctrl.write(addr, data)
            await RisingEdge(dut.ap_clk)

    def check_result(self) -> None:
        """Check result of testbench."""
        _logger.info("Check output")
        for i in range(DATA_LEN):
            # get output in bytes and convert bytes to float
            out_bytes = self.gmem_C.read_word(i*4, ws=4).to_bytes(4, "big")
            out_float = bytes_to_float(out_bytes)
            assert math.isclose(float(i)*2, out_float, rel_tol=1e-5)

    async def run(self, deley_count: int = 100) -> None:
        """Run testbench."""
        adder_run = await cocotb.start(self.adder.run())  # adder coroutine

        await self.reset()  # reset testbench

        # set ap_start
        _logger.info("Set ap_start")
        await self.ctrl.write(0x00, b'\x01')
        await RisingEdge(self.dut.ap_clk)

        # wait until ap_done is set or timeout
        ap_done = 0
        while ap_done == 0:
            byte = await self.ctrl.read_byte(0x00)
            ap_done = byte // 2 % 2  # get bit[1](ap_done) of byte
            deley_count -= 1
            if deley_count == 0:
                raise TimeoutError("Timeout before ap_done is set")

        self.check_result()

        adder_run.kill()  # stop adder to let the test exit


@cocotb.test()
async def test(dut: HierarchyObject) -> None:
    """Main testbench.

    Args:
        delay_count: timeout delay in case ap_done could never been set
    """
    vadd_test = VecaddTest(dut)
    await vadd_test.run(deley_count=100)


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
    source_paths.append("./fp_blackbox.sv")

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
