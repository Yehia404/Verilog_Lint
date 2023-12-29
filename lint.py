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
        # self.check_non_full_parallel_case(verilog_code)
        self.check_multi_driven_registers(verilog_code)
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
        declaration_pattern =r'\b(?:reg|wire|output)\s*([^;]+)\b'
        for line_number, line in enumerate(verilog_code, start=1):
            matches = re.findall(declaration_pattern, line)
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
        


    # def check_multi_driven_registers(self, verilog_code):
    #     always_block_pattern= r'\balways\s+@.*?\bbegin\b\n.*?\bend\b'
    #     for line_number, line in enumerate(verilog_code, start=1):
    #         matches = re.findall(always_block_pattern, line)
    #         print(matches)



    # def check_multi_driven_registers(self, verilog_code):
    #     register_assignments = {}
    #     always_blocks = self.extract_always_blocks(verilog_code)
    #     for always_block in always_blocks:
    #         # print(always_block)
    #         assignments = self.extract_register_assignments(always_block,verilog_code)

    #         for assignment in assignments:
    #             register_name = assignment[0]
    #             line_number = assignment[1]

    #             if register_name not in register_assignments:
    #                 register_assignments[register_name] = line_number
    #             else:
    #                 previous_line_number = register_assignments[register_name]
    #                 if previous_line_number != line_number:
    #                     self.errors['Multi-Driven Registers'].append(
    #                         (line_number, f"Register '{register_name}' is assigned in multiple always blocks. "
    #                                     f"Previous assignment at line {previous_line_number}."))

    
    # def extract_always_blocks(self, verilog_code):
    #     verilog_code_str = ''.join(verilog_code)  # Join the lines into a single string
    #     always_block_pattern = r'\balways\s+@.*?\bend\b'
    #     always_blocks = re.findall(always_block_pattern, verilog_code_str, re.DOTALL)
    #     return always_blocks

    # def extract_register_assignments(self, always_block):
    #     register_assignment_pattern = r'\b(\w+)\s*=\s*[^;]+\b'
    #     assignments = re.findall(register_assignment_pattern, always_block)
    #     line_number = always_block.count('\n') + 1
    #     return [(assignment, line_number) for assignment in assignments]

    def check_multi_driven_registers(self, verilog_code):
        register_assignments = {}
        verilog_code_str = ''.join(verilog_code)
        # print(verilog_code_str)
        lines = verilog_code_str.splitlines()

        for line_number, line in enumerate(lines, start=1):
            if re.search(r'\balways\s*@', line):
                always_block = self.extract_always_block(lines, line_number)
                # print(always_block)
                assignments = self.extract_register_assignments(always_block, line_number)

                for assignment in assignments:
                    register_name = assignment[0]
                    register_line_number = assignment[1]

                    if register_name not in register_assignments:
                        register_assignments[register_name] = register_line_number
                    else:
                        previous_line_number = register_assignments[register_name]
                        if previous_line_number != register_line_number:
                            self.errors['Multi-Driven Registers'].append(
                                (register_line_number, f"Register '{register_name}' is assigned in multiple always blocks. "
                                                       f"Previous assignment at line {previous_line_number}."))

    def extract_always_block(self, lines, line_number):
        always_block = []
        indent_level = self.get_indent_level(lines[line_number - 1])
        for line in lines[line_number - 1:]:
            if self.get_indent_level(line) <= indent_level and re.search(r'\bend\b', line):
                always_block.append(line)
                break
            always_block.append(line)

        return ''.join(always_block)

    def get_indent_level(self, line):
        return len(line) - len(line.lstrip())

    def extract_register_assignments(self, always_block, line_number):
        register_assignment_pattern = r'\b(\w+)\s*=\s*[^;]+\b'
        assignments = re.findall(register_assignment_pattern, always_block)
        return [(assignment, line_number+1) for assignment in assignments]



    
    # def check_non_full_parallel_case(self, verilog_code):
    #     non_full_parallel_patterns = [
    #         (r'\bif\s*\([^)]+\)\s*begin\s*(?:\n\s*[^{]+\n)+\s*end\b', "If statement"),
    #         (r'\bcase\s*\([^)]+\)\s*(?:\n\s*[^{]+\n)+\s*endcase\b', "Case statement")
    #     ]

    #     for line_number, line in enumerate(verilog_code, start=1):
    #         for pattern, violation_type in non_full_parallel_patterns:
    #             matches = re.findall(pattern, line, re.MULTILINE)
    #             for match in matches:
    #                 body = match.strip()
    #                 body_lines = body.split('\n')
    #                 body_lines = [line.strip() for line in body_lines if line.strip() != '']

    #                 if violation_type == "If statement":
    #                     # Check if the if statement is incomplete (missing else part)
    #                     if "else" not in body:
    #                         self.errors['Non Full/Parallel'].append((line_number, "Incomplete if statement (missing else part)."))

    #                     # Check if there are matching conditions in if and elseif
    #                     conditions = [re.search(r'if\s*\((.*?)\)', line).group(1) for line in body_lines if "if" in line]
    #                     if len(set(conditions)) != len(conditions):
    #                         self.errors['Non Full/Parallel'].append((line_number, "Matching conditions in if statement."))

    #                 elif violation_type == "Case statement":
    #                     # Check if the case statement has a missing default or non-full cases
    #                     case_body = body_lines[1:-1]  # Exclude the first and last lines (case and endcase)
    #                     num_cases = len(case_body)
    #                     has_default = any("default" in line for line in case_body)

    #                     if num_cases == 0 or not has_default:
    #                         self.errors['Non Full/Parallel'].append((line_number, "Incomplete case statement (missing default or cases)."))

    #                     # Check if there are matching cases
    #                     cases = [re.search(r'(\bcase\b|\bdefault\b)\s*\((.*?)\)', line).group(2) for line in case_body]
    #                     if len(set(cases)) != len(cases):
    #                         self.errors['Non Full/Parallel'].append((line_number, "Matching cases in case statement."))





    def generate_report(self, report_file):
        with open(report_file, 'w') as f:
            for violation, lines in self.errors.items():
                f.write(f"{violation}:\n")
                for line_number, line in lines:
                    f.write(f"\tLine {line_number}: {line}\n")
    
# Example usage
linter = VerilogLinter()
linter.parse_verilog('multi.v')
linter.generate_report('lint_report.txt')