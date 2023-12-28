module dff_mux(
input clk,
input sel,
input rst,
input a,
input b,
output out
);

always @(posedge clk or posedge rst) begin
if(rst) begin
    out <= 0;
end 
else begin
    out <= (sel)? a: b;
end
end
endmodule