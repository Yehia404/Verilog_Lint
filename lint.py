import re
from collections import defaultdict

class VerilogLinter:
    def __init__(self):
        self.errors = defaultdict(list)
    
    def parse_verilog(self, file_path):
        with open(file_path, 'r') as f:
            verilog_code = f.readlines()
        
        # Perform parsing logic here
        
        self.check_arithmetic_overflow(verilog_code)
        self.check_non_full_parallel_case(verilog_code)
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

    def check_non_full_parallel_case(self, verilog_code):
        non_full_parallel_patterns = [
            (r'\bif\s*\([^)]+\)\s*begin\s*(?:\n\s*[^{]+\n)+\s*end\b', "If statement"),
            (r'\bcase\s*\([^)]+\)\s*(?:\n\s*[^{]+\n)+\s*endcase\b', "Case statement")
        ]

        for line_number, line in enumerate(verilog_code, start=1):
            for pattern, violation_type in non_full_parallel_patterns:
                matches = re.findall(pattern, line, re.MULTILINE)
                for match in matches:
                    body = match.strip()
                    body_lines = body.split('\n')
                    body_lines = [line.strip() for line in body_lines if line.strip() != '']

                    if violation_type == "If statement":
                        # Check if the if statement is incomplete (missing else part)
                        if "else" not in body:
                            self.errors['Non Full/Parallel'].append((line_number, "Incomplete if statement (missing else part)."))

                        # Check if there are matching conditions in if and elseif
                        conditions = [re.search(r'if\s*\((.*?)\)', line).group(1) for line in body_lines if "if" in line]
                        if len(set(conditions)) != len(conditions):
                            self.errors['Non Full/Parallel'].append((line_number, "Matching conditions in if statement."))

                    elif violation_type == "Case statement":
                        # Check if the case statement has a missing default or non-full cases
                        case_body = body_lines[1:-1]  # Exclude the first and last lines (case and endcase)
                        num_cases = len(case_body)
                        has_default = any("default" in line for line in case_body)

                        if num_cases == 0 or not has_default:
                            self.errors['Non Full/Parallel'].append((line_number, "Incomplete case statement (missing default or cases)."))

                        # Check if there are matching cases
                        cases = [re.search(r'(\bcase\b|\bdefault\b)\s*\((.*?)\)', line).group(2) for line in case_body]
                        if len(set(cases)) != len(cases):
                            self.errors['Non Full/Parallel'].append((line_number, "Matching cases in case statement."))





    def generate_report(self, report_file):
        with open(report_file, 'w') as f:
            for violation, lines in self.errors.items():
                f.write(f"{violation}:\n")
                for line_number, line in lines:
                    f.write(f"\tLine {line_number}: {line}\n")
    
# Example usage
linter = VerilogLinter()
linter.parse_verilog('fulladder.v')
linter.generate_report('lint_report.txt')