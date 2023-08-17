#include <cstdio>
#include <cassert>
#include "read_and_write.h"


int main() {
    data_t mem_0[DATA_LEN];
    data_t mem_1[DATA_LEN];
    for (int i = 0; i < DATA_LEN; i++) {
        mem_0[i] = data_t(i);
        mem_1[i] = data_t(i);
    }

    data_t mem_2[DATA_LEN];
    top(mem_0, mem_1, mem_2);

    for (int i = 0; i < DATA_LEN; i++) {
        assert (abs(mem_2[i] - 2 * data_t(i) < EPSILON));
    }

    printf("PASSED\n");
    return 0;
}
