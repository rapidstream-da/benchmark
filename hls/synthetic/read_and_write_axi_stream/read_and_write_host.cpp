#include <cstdio>
#include <cassert>
#include "read_and_write.h"


int main() {
    hls::stream<data_t> mem_0;
    hls::stream<data_t> mem_1;

    for (int i = 0; i < DATA_LEN; i++) {
        mem_0.write(i);
    }

    top(mem_0, mem_1);

    for (int i = 0; i < DATA_LEN; i++) {
        assert (mem_1.read() == i);
    }

    printf("PASSED\n");
    return 0;
}
