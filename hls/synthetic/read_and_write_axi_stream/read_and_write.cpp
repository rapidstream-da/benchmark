#include "read_and_write.h"

void load(hls::stream<data_t>& mem, hls::stream<data_t>& fifo_1) {
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        fifo_1.write(mem.read());
    }
}

void compute(hls::stream<data_t>& fifo_1, hls::stream<data_t>& fifo_2) {
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        data_t tmp = fifo_1.read();
        fifo_2.write(tmp);
    }
}

void store(hls::stream<data_t>& mem, hls::stream<data_t>& fifo_2) {
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        mem.write(fifo_2.read());
    }
}

void top(hls::stream<data_t>& mem_0, hls::stream<data_t>& mem_1)
{
#pragma HLS INTERFACE axis port=mem_0,mem_1

#pragma HLS DATAFLOW disable_start_propagation

  hls::stream<data_t> fifo_1;
  hls::stream<data_t> fifo_2;
  #pragma HLS STREAM variable=fifo_1 depth=2
  #pragma HLS STREAM variable=fifo_2 depth=2

  load(mem_0, fifo_1);
  compute(fifo_1, fifo_2);
  store(mem_1, fifo_2);

}
