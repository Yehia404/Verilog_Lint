import re
from collections import defaultdict

class VerilogLinter:
    def __init__(self):
        self.errors = defaultdict(list)
        self.initialized_registers = set()
        self.declarations = {}

    def parse_verilog(self, file_path):
        with open(file_path, 'r') as f:
            verilog_code = f.readlines()
        
        # Perform parsing logic here
        
        self.check_arithmetic_overflow(verilog_code)
        self.check_uninitialized_registers(verilog_code)
        self.check_multi_driven_registers(verilog_code)
        self.check_inferred_latches(verilog_code)
        # Implement similar logic for other violations
        
    #---------------------------------------------------------------------------------------------------------------------------------------   
    # def check_arithmetic_overflow(self, verilog_code):
    #     overflow_pattern = r'\b(\w+)\s*=\s*(\w+)\s*([+\-*/])\s*(\w+)\b'
    #     for line_number, line in enumerate(verilog_code, start=1):
    #         matches = re.findall(overflow_pattern, line)
    #         for match in matches:
    #             signal = match[0]
    #             op1 = match[1]
    #             operator = match[2]
    #             op2 = match[3]
                
    #             # Check for overflow condition and add error if necessary
    #             if operator in ['+', '-']:
    #                 self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may overflow."))
    #             elif operator == '*':
    #                 self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may cause multiplication overflow."))
    #             elif operator == '/':
    #                 self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may cause division overflow."))
    #---------------------------------------------------------------------------------------------------------------------------------------
    def check_arithmetic_overflow(self, verilog_code):
        variable_bits = {}
        overflow_pattern = r'\b(\w+)\s*=\s*(\w+)\s*([+\-/])\s(\w+)\b'
        register_pattern = r'\b(input|output|reg|output \s* reg|wire)\s*(\[\d+:\d+\])?\s*(\w+)\b'
        for variable in verilog_code:
            matches = re.findall(register_pattern, variable)
            for match in matches:
                variable_name = match[2]
                variable_bit = match[1]
                if variable_bit == '':
                    variable_bits[variable_name] = 1
                else:
                    num1 = int(variable_bit[1])
                    num2 = int(variable_bit[3])
                    result = abs(num1 - num2) + 1
                    variable_bits[variable_name] = result
        for line_number, operation in enumerate(verilog_code, start=1):
            matches = re.findall(overflow_pattern, operation)

            for match in matches:
                signal = match[0]
                op1 = match[1]
                operator = match[2]
                op2 = match[3]
                
                # Check for overflow condition and add error if necessary
                if operator  == '+' and variable_bits[signal] <= max(variable_bits[op1], variable_bits[op2]):
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may overflow."))
                elif operator == '-' and variable_bits[signal] < max(variable_bits[op1], variable_bits[op2]):
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may overflow."))
                elif operator == '*' and variable_bits[signal] < variable_bits[op1] + variable_bits[op2]:
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may cause multiplication overflow."))
                elif operator == '/' and variable_bits[signal] < variable_bits[op1]:
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may cause division overflow."))
    #---------------------------------------------------------------------------------------------------------------------------------------
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

    #---------------------------------------------------------------------------------------------------------------------------------------
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

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def check_inferred_latches(self, verilog_code):
        verilog_code_str = ''.join(verilog_code)
        lines = verilog_code_str.splitlines()

        self.process_declarations(lines)

        for line_number, line in enumerate(lines, start=1):
            if re.search(r'\balways\s+@', line):
                always_block = self.extract_always_block(lines, line_number)
                if re.search(r'\bif\b', always_block):
                    if not self.has_else_branch(always_block):
                        self.errors['Inferred Latches'].append(
                            (line_number, "Inferred latch found: 'if' statement without an 'else' branch."))

                if re.search(r'\bcase\b', always_block):
                    if not self.has_complete_cases(always_block):
                         
                        if not self.has_default_case(always_block):
                            self.errors['Inferred Latches'].append(
                                (line_number, "Inferred latch found: 'case' statement without a default case."))
                       

    def process_declarations(self, lines):
        for line in lines:
            match = re.search(r'\breg\b\s*\[(\d+):(\d+)\]\s*(\w+)\s*;', line)
            if match:
                start_bit = int(match.group(1))
                end_bit = int(match.group(2))
                name = match.group(3)
                size = start_bit - end_bit + 1
                self.declarations[name] = size
            if re.search(r'\bendmodule\b', line):
                break


    def has_else_branch(self, always_block):
        if_match = re.findall(r'\bif\s*\([^)]+\)', always_block)
        for if_statement in if_match:
            if re.search(r'else', if_statement):
                return True

        return False

    def has_default_case(self, always_block):
        case_match = re.search(r'\bcase\s*\([^)]+\)', always_block)
        if case_match:
            case_block = always_block[case_match.end():]
            return re.search(r'\bdefault\b', case_block)

        return True

    def has_complete_cases(self, always_block):
        case_match = re.search(r'\bcase\s*\(([^)]+)\)', always_block)        
        if case_match:
            variable_name=case_match.group(1)
            case_block = always_block[case_match.end():]
            case_statements = re.findall(r'(\d+\'[bB][01]+)\s*:\s*', case_block, re.DOTALL)
            if case_statements:
                condition_bits = self.declarations.get(variable_name, 1)  # Use get() with a default value of 1
                if len(case_statements) != (2 ** condition_bits):
                    return False

        return True

    #---------------------------------------------------------------------------------------------------------------------------------------

    def generate_report(self, report_file):
        with open(report_file, 'w') as f:
            for violation, lines in self.errors.items():
                f.write(f"{violation}:\n")
                for line_number, line in lines:
                    f.write(f"\tLine {line_number}: {line}\n")
    
# Example usage
linter = VerilogLinter()
linter.parse_verilog('infer.v')
linter.generate_report('lint_report.txt')