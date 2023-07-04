#include "read_and_write.h"

void load(data_t mem[DATA_LEN], hls::stream<data_t>& fifo_1, int data_len) {
    for (int i = 0; i < data_len; i++) {
        #pragma HLS pipeline II=1
        fifo_1.write(mem[i]);
    }
}

void compute(hls::stream<data_t>& fifo_1, hls::stream<data_t>& fifo_2, int data_len) {
    for (int i = 0; i < data_len; i++) {
        #pragma HLS pipeline II=1
        data_t tmp = fifo_1.read();
        fifo_2.write(tmp);
    }
}

void store(data_t mem[DATA_LEN], hls::stream<data_t>& fifo_2, int data_len) {
    for (int i = 0; i < data_len; i++) {
        #pragma HLS pipeline II=1
        mem[i] = fifo_2.read();
    }
}

void top(
    data_t mem_0[DATA_LEN],
    data_t mem_1[DATA_LEN],
    int data_len1,
    int data_len2
) {
#pragma HLS INTERFACE m_axi port=mem_0 offset=slave bundle=gmem_A depth=DATA_LEN
#pragma HLS INTERFACE m_axi port=mem_1 offset=slave bundle=gmem_B depth=DATA_LEN
#pragma HLS INTERFACE s_axilite port=mem_0 bundle=control
#pragma HLS INTERFACE s_axilite port=mem_1 bundle=control
#pragma HLS INTERFACE s_axilite port=data_len1 bundle=control
#pragma HLS INTERFACE s_axilite port=data_len2 bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

#pragma HLS DATAFLOW disable_start_propagation

  hls::stream<data_t> fifo_1;
  hls::stream<data_t> fifo_2;
  #pragma HLS STREAM variable=fifo_1 depth=2
  #pragma HLS STREAM variable=fifo_2 depth=2

  load(mem_0, fifo_1, data_len1);
  compute(fifo_1, fifo_2, data_len1);
  store(mem_1, fifo_2, data_len2);

}
