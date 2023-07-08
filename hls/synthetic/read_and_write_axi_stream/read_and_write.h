#ifndef READ_AND_WRITE_H
#define READ_AND_WRITE_H

#include <hls_stream.h>

using data_t = int;
#define DATA_LEN 256

void top(hls::stream<data_t>& mem_0, hls::stream<data_t>& mem_1);

#endif
