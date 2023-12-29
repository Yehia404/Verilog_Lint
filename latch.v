module Test;
  reg [1:0] a;
  reg [2:0] b;
  reg out;

  always @(a, b)
  begin
    if (a[0] & b[0])
      out <= 1;
    else if (a[1] | b[1])
      out <= 0;
  end

  always @(a)
  begin
    case (a)
      2'b00: out <= 0;
      2'b01: out <= 1;
      2'b10: out <= 0;
    endcase
  end

  always @(a)
  begin
    case (a)
      2'b00: out <= 0;
      2'b01: out <= 1;
    endcase
  end

  always @(b)
  begin
    case (b)
      2'b00: out <= 0;
      2'b01: out <= 1;
      2'b10: out <= 0;
      2'b11: out <= 1;
    endcase
  end
endmodule