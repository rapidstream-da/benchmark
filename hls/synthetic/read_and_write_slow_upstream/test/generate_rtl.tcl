open_project project1.prj -reset

add_files ../read_and_write.h
add_files ../read_and_write.cpp
add_files -tb ../read_and_write_host.cpp

set_top top
open_solution solution1
set_part xcu250-figd2104-2L-e
create_clock -period 300.000000MHz -name default
set_clock_uncertainty 27.000000%
config_interface -m_axi_addr64=True

csim_design
csynth_design

close_project
puts "HLS completed successfully"
exit
