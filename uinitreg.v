module uinitreg();
reg [3:0] a;
reg b = 1;
reg [7:0] c;

always @(*) begin
    a = b;  
    b = c;
end

endmodule