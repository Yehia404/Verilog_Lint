module ExampleModule;
  reg s1; 
  reg s2; 
  reg s3;  
  

  initial begin
    s1 = 0;
    s2 = s1 + 1;
    s3 = s2 * 2;
  end

  always @(posedge clk) begin
    s4 = s1 + s2;  
    s5 = 1;        
    s6 = s4 * s5;  
    
   end

  

endmodule
