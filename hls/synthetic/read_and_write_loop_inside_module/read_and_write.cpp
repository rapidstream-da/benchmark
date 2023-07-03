#include "read_and_write.h"

void load(data_t mem[DATA_LEN], hls::stream<data_t>& fifo_1) {
    #pragma HLS inline off
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        fifo_1.write(mem[i]);
    }
}

void compute(hls::stream<data_t>& fifo_1, hls::stream<data_t>& fifo_2) {
    #pragma HLS inline off
    for (int i = 0; i < DATA_LEN / 2; i++) {
        #pragma HLS pipeline II=1
        data_t tmp = fifo_1.read();
        fifo_2.write(tmp);
    }
}

void store(data_t mem[DATA_LEN], hls::stream<data_t>& fifo_2) {
    #pragma HLS inline off
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        mem[i] = fifo_2.read();
    }
}

void wrapper(hls::stream<data_t>& fifo_1, hls::stream<data_t>& fifo_2) {
#pragma HLS DATAFLOW disable_start_propagation

    hls::stream<data_t> fifo_3;
    #pragma HLS STREAM variable=fifo_3 depth=2

    for (int i = 0; i < 2; i++) {
#pragma HLS DATAFLOW disable_start_propagation
        compute(fifo_1, fifo_3);
        compute(fifo_3, fifo_2);
    }
}

void top(data_t mem_0[DATA_LEN], data_t mem_1[DATA_LEN])
{
#pragma HLS INTERFACE m_axi port=mem_0 offset=slave bundle=gmem_A depth=DATA_LEN
#pragma HLS INTERFACE m_axi port=mem_1 offset=slave bundle=gmem_B depth=DATA_LEN
#pragma HLS INTERFACE s_axilite port=mem_0 bundle=control
#pragma HLS INTERFACE s_axilite port=mem_1 bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

    hls::stream<data_t> fifo_1;
    hls::stream<data_t> fifo_2;
    #pragma HLS STREAM variable=fifo_1 depth=2
    #pragma HLS STREAM variable=fifo_2 depth=2

#pragma HLS DATAFLOW disable_start_propagation

    load(mem_0, fifo_1);
    wrapper(fifo_1, fifo_2);
    store(mem_1, fifo_2);

}
