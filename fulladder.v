module adder (X, Y, S);
input    X;
input     Y;
output   [1:0]   S;

assign S = X   *   Y;
endmodule
