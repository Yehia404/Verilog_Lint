module overflow (X, Y, S, Z);
input  X;
input  [1:0]Y;
output S;
output Z;

assign S = X + Y;
assign Z = X * Y;
endmodule
