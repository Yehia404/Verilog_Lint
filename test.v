module test(x,y,a,b,c,d,s,z,r);
input x;
input y;
input [1:0]a;
input b;
input c;
input d;
output s;
output z;
output [1:0] r;
reg s1;
reg s2;
reg s3;
reg [1:0]ct;
reg out;


//Arithmetic Overflow
assign s = x + y;   // Addition Overflow
assign z = a * b;   // Multiplication Overflow
assign r = c + d;   // No Overflow


//Uninitialized Registers and Multi-Driven Registers
always @(posedge clk) begin
    s3 = s1 + s2;
    s4 = s5  
    s5 = 1;         
end

always @(posedge clk) begin
    s3 = s1;
end

//Non Full/Parallel Case and Infer Latch
always @(b, c) begin
    if (b)
      out <= 1;
    else if (c)
      out <= 0;             //Missing else (Infer Latch)
end

always @(ct) begin
  case (ct)
    2'b00: out <= 0;
    2'b01: out <= 1;
    2'b10: out <= 0;
  endcase                 //Incomplete cases (Infer Latch) and Not Full
end

always @(ct) begin
  case (ct)
    2'b00: out <= 0;
    2'b01: out <= 1;
    2'b10: out <= 1;
    2'b11: out <= 0;      //Complete Case and Full
  endcase
end

always @(a) begin
  case (a)
    2'b00: out <= 0;
    default: out <= 1;    //Complete has a default and Full
  endcase
end

always @(a) begin
  case (a)
    2'b00: out <= 0;
    2'b01: out <= 1;
    2'b01: out <= 1;
    2'b10: out <= 0;
    2'b11: out <= 1;      //Full but not parallel
  endcase
end




endmodule