module top_fadd_32ns_32ns_32_7_full_dsp_1_ip(
    aclk,
    aclken,
    s_axis_a_tvalid,
    s_axis_a_tdata,
    s_axis_b_tvalid,
    s_axis_b_tdata,
    m_axis_result_tvalid,
    m_axis_result_tdata
);
    input logic aclk;
    input logic aclken;
    input logic s_axis_a_tvalid;
    input logic [31:0] s_axis_a_tdata;
    input logic s_axis_b_tvalid;
    input logic [31:0] s_axis_b_tdata;
    output logic m_axis_result_tvalid;
    output logic [31:0] m_axis_result_tdata;
endmodule
