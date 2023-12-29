module Test;
  reg [7:0] reg1;
  reg [7:0] reg2;

  always @ (posedge clk)begin
    reg1 = data1;
  end

  always @ (posedge clk)begin
    reg2 = data2;
    end
  always @ (posedge clk)begin
    reg1 = data3;
    end

endmodule