"""Floating point ip simulator (single precision adder)."""

import struct
from queue import Queue

from cocotb.binary import BinaryValue
from cocotb.handle import ModifiableObject
from cocotb.triggers import RisingEdge


HIGHIMP = "z"
HIGHIMP32 = "z" * 32
UNKNOWN = "x"


def bytes_to_float(num: bytes, byteorder: str = "big") -> float:
    """Convert bytes to float."""
    assert byteorder in {"big", "little"}
    _format = "<f" if byteorder == "little" else ">f"
    return struct.unpack(_format, num)[0]


def float_to_bytes(num: float, byteorder: str = "big") -> bytes:
    """Convert float to bytes."""
    assert byteorder in {"big", "little"}
    _format = "<f" if byteorder == "little" else ">f"
    return bytes(struct.pack(_format, num))


class fadd:
    """Floating point ip add simulator."""

    def __init__(
        self,
        aclk: ModifiableObject,
        aclk_en: ModifiableObject,
        a_valid: ModifiableObject,
        a_data: ModifiableObject,
        b_valid: ModifiableObject,
        b_data: ModifiableObject,
        out_valid: ModifiableObject,
        out_data: ModifiableObject,
        delay: int,
    ):
        """Initialize fadd class."""
        self.aclk = aclk
        self.aclk_en = aclk_en
        self.a_valid = a_valid
        self.a_data = a_data
        self.b_valid = b_valid
        self.b_data = b_data
        self.out_valid = out_valid
        self.out_data = out_data
        self.out_valid.value = 0
        self.delay_queue = Queue(delay - 1)

        # fill shift_reg
        for _i in range(delay - 1):
            binary_value_highimp32 = BinaryValue()
            binary_value_highimp32.assign(HIGHIMP32)
            self.delay_queue.put((BinaryValue("0"), binary_value_highimp32),
                                 block=False)
        assert self.delay_queue.full()

    def _calc_output(self) -> tuple[BinaryValue, BinaryValue]:
        # Calculate valid
        valid_out = (
            BinaryValue("1")
            if self.a_valid.value == 1 and self.b_valid.value == 1
            else BinaryValue("0")
        )

        # Calculate data
        ab_value = self.a_data.value.binstr + self.b_data.value.binstr
        if HIGHIMP in ab_value or UNKNOWN in ab_value:
            binary_value_undef32 = BinaryValue()
            binary_value_undef32.assign(HIGHIMP32)
            data_out = binary_value_undef32

        else:
            a = bytes_to_float(self.a_data.value.buff)
            b = bytes_to_float(self.b_data.value.buff)
            data_out = BinaryValue(float_to_bytes(a + b))

        return (valid_out, data_out)

    # Split valid data
    async def run(self) -> None:
        """Run Floating point ip."""
        while True:
            # Stall if clock not enabled
            if UNKNOWN in self.aclk_en.value.binstr or self.aclk_en == 0:
                await RisingEdge(self.aclk)
                continue

            assert self.delay_queue.full()

            # Assign signals
            valid_out, data_out = self.delay_queue.get(block=False)
            self.out_valid.value = valid_out
            self.out_data.value = data_out

            # Calculate new result and put into delay queue
            result = self._calc_output()
            self.delay_queue.put(result, block=False)

            await RisingEdge(self.aclk)
