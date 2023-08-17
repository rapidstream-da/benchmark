#include "read_and_write.h"

void load(data_t mem[DATA_LEN], hls::stream<data_t>& fifo_0) {
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        fifo_0.write(mem[i]);
    }
}

void compute(hls::stream<data_t>& fifo_0, hls::stream<data_t>& fifo_1, hls::stream<data_t>& fifo_2) {
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        if (!fifo_0.empty() && !fifo_1.empty()) {
            data_t tmp0, tmp1;
            fifo_0.read_nb(tmp0);
            fifo_1.read_nb(tmp1);

            fifo_2.write(tmp0 + tmp1);
        }
    }
}

void store(data_t mem[DATA_LEN], hls::stream<data_t>& fifo_2) {
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        mem[i] = fifo_2.read();
    }
}

void top(data_t mem_0[DATA_LEN], data_t mem_1[DATA_LEN], data_t mem_2[DATA_LEN])
{
#pragma HLS INTERFACE m_axi port=mem_0 offset=slave bundle=gmem_A depth=DATA_LEN
#pragma HLS INTERFACE m_axi port=mem_1 offset=slave bundle=gmem_B depth=DATA_LEN
#pragma HLS INTERFACE m_axi port=mem_2 offset=slave bundle=gmem_C depth=DATA_LEN
#pragma HLS INTERFACE s_axilite port=mem_0 bundle=control
#pragma HLS INTERFACE s_axilite port=mem_1 bundle=control
#pragma HLS INTERFACE s_axilite port=mem_2 bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

#pragma HLS DATAFLOW disable_start_propagation

  hls::stream<data_t> fifo_0;
  hls::stream<data_t> fifo_1;
  hls::stream<data_t> fifo_2;
  #pragma HLS STREAM variable=fifo_0 depth=2
  #pragma HLS STREAM variable=fifo_1 depth=2
  #pragma HLS STREAM variable=fifo_2 depth=2

  load(mem_0, fifo_0);
  load(mem_1, fifo_1);
  compute(fifo_0, fifo_1, fifo_2);
  store(mem_2, fifo_2);

}
