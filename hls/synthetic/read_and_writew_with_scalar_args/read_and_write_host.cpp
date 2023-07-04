#include <cstdio>
#include <cassert>
#include "read_and_write.h"


int main() {
    data_t mem_0[DATA_LEN];
    for (int i = 0; i < DATA_LEN; i++) {
        mem_0[i] = i;
    }

    data_t mem_1[DATA_LEN];
    top(mem_0, mem_1, DATA_LEN, DATA_LEN);

    for (int i = 0; i < DATA_LEN; i++) {
        assert (mem_1[i] == i);
    }

    printf("PASSED\n");
    return 0;
}
