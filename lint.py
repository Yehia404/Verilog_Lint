import re
from collections import defaultdict

class VerilogLinter:
    def __init__(self):
        self.errors = defaultdict(list)
        self.initialized_registers = set()
    
    def parse_verilog(self, file_path):
        with open(file_path, 'r') as f:
            verilog_code = f.readlines()
        
        # Perform parsing logic here
        
        self.check_arithmetic_overflow(verilog_code)
        self.check_uninitialized_registers(verilog_code)
        # Implement similar logic for other violations
        
       
    def check_arithmetic_overflow(self, verilog_code):
        overflow_pattern = r'\b(\w+)\s*=\s*(\w+)\s*([+\-*/])\s*(\w+)\b'
        for line_number, line in enumerate(verilog_code, start=1):
            matches = re.findall(overflow_pattern, line)
            for match in matches:
                signal = match[0]
                op1 = match[1]
                operator = match[2]
                op2 = match[3]
                
                # Check for overflow condition and add error if necessary
                if operator in ['+', '-']:
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may overflow."))
                elif operator == '*':
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may cause multiplication overflow."))
                elif operator == '/':
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may cause division overflow."))
 

    def check_uninitialized_registers(self,verilog_code):
        declaration_pattern =r'\b(?:reg|wire)\s*([^;]+)\b'
        for line_number, line in enumerate(verilog_code, start=1):
            matches = re.findall(declaration_pattern, line)
            print(matches)
            for match in matches:
                signal_names = re.findall(r'\b(\w+)\b', match)
                for signal in signal_names:
                    self.initialized_registers.add(signal)
                        
                
        usage_pattern = r'\b(\w+)\s*=\s*([^;]+)\b'
        for line_number, line in enumerate(verilog_code, start=1):
            matches = re.findall(usage_pattern, line)
            for match in matches:
                signal = match[0]
                
            

                if signal not in self.initialized_registers:
                    self.errors['Uninitialized Register Usage'].append((line_number, f"Register '{signal}' used before initialization."))
        
    
    
    
    
    def generate_report(self, report_file):
        with open(report_file, 'w') as f:
            for violation, lines in self.errors.items():
                f.write(f"{violation}:\n")
                for line_number, line in lines:
                    f.write(f"\tLine {line_number}: {line}\n")
    
# Example usage
linter = VerilogLinter()
linter.parse_verilog('Uninitializedreg.v')
linter.generate_report('lint_report.txt')