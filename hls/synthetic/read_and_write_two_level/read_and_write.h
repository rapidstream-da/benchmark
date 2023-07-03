#ifndef READ_AND_WRITE_H
#define READ_AND_WRITE_H

#include <hls_stream.h>

using data_t = int;
#define DATA_LEN 32

void top(data_t mem_0[DATA_LEN], data_t mem_1[DATA_LEN]);

#endif
