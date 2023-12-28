module mux_always (in0, in1, sel, out);
input in0, in1, sel;
output reg out;

always @(*)
if (sel) begin
    out = in1;
end

endmodule