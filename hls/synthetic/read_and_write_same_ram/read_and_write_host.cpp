#include <cstdio>
#include <cassert>
#include "read_and_write.h"


int main() {
    data_t mem_0[DATA_LEN];
    for (int i = 0; i < DATA_LEN; i++) {
        mem_0[i] = i;
    }

    top(mem_0);

    for (int i = 0; i < DATA_LEN; i++) {
        assert (mem_0[i] == i + 1);
    }

    printf("PASSED\n");
    return 0;
}
