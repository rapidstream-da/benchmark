#include "read_and_write.h"

void load(data_t mem[DATA_LEN*LOOP_ITER], hls::stream<data_t>& fifo_1, int offset) {
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        fifo_1.write(mem[i+offset]);
    }
}

void compute(hls::stream<data_t>& fifo_1, hls::stream<data_t>& fifo_2) {
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        if (!fifo_1.empty()) {
            data_t tmp;
            fifo_1.read_nb(tmp);
            fifo_2.write(tmp);
        }
    }
}

void store(data_t mem[DATA_LEN*LOOP_ITER], hls::stream<data_t>& fifo_2, int offset) {
    for (int i = 0; i < DATA_LEN; i++) {
        #pragma HLS pipeline II=1
        mem[i+offset] = fifo_2.read();
    }
}

void top(data_t mem_0[DATA_LEN*LOOP_ITER], data_t mem_1[DATA_LEN*LOOP_ITER])
{
#pragma HLS INTERFACE m_axi port=mem_0 offset=slave bundle=gmem_A depth=DATA_LEN*LOOP_ITER
#pragma HLS INTERFACE m_axi port=mem_1 offset=slave bundle=gmem_B depth=DATA_LEN*LOOP_ITER
#pragma HLS INTERFACE s_axilite port=mem_0 bundle=control
#pragma HLS INTERFACE s_axilite port=mem_1 bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
#pragma HLS DATAFLOW disable_start_propagation

    hls::stream<data_t> fifo_1;
    hls::stream<data_t> fifo_2;
    #pragma HLS STREAM variable=fifo_1 depth=2
    #pragma HLS STREAM variable=fifo_2 depth=2

    for(int i = 0; i < LOOP_ITER; i++) {
#pragma HLS DATAFLOW disable_start_propagation
        load(mem_0, fifo_1, i*DATA_LEN);
        compute(fifo_1, fifo_2);
        store(mem_1, fifo_2, i*DATA_LEN);
    }

}
