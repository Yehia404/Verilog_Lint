module mux_assign (in0, in1, sel, out);
input in0, in1, sel;
output out;

assign out = (sel)? in1: in0;
endmodule