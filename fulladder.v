module adder (X, Y,S);
input X;
input [1:0] Y;
output [2:0] S;

assign S = X * Y;
endmodule
