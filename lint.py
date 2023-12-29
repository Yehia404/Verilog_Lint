import re
from collections import defaultdict

class VerilogLinter:
    def __init__(self):
        self.errors = defaultdict(list)
        self.initialized_registers = set()
        self.variable_bits = {}
    
    def parse_verilog(self, file_path):
        with open(file_path, 'r') as f:
            verilog_code = f.readlines()
        
        # Perform parsing logic here
        
        self.check_arithmetic_overflow(verilog_code)
        self.check_uninitialized_registers(verilog_code)
        # self.check_non_full_parallel_case(verilog_code)
        self.check_multi_driven_registers(verilog_code)
        self.check_inferred_latches(verilog_code)
        # Implement similar logic for other violations
        
       
    def check_arithmetic_overflow(self, verilog_code):
        overflow_pattern = r'\b(\w+)\s*=\s*(\w+)\s*([+\-/])\s(\w+)\b'
        register_pattern = r'\b(input|output|reg|output \s* reg|wire)\s*(\[\d+:\d+\])?\s*(\w+)\b'
        for variable in verilog_code:
            matches = re.findall(register_pattern, variable)
            for match in matches:
                variable_name = match[2]
                variable_bit = match[1]
                if variable_bit == '':
                    self.variable_bits[variable_name] = 1
                else:
                    num1 = int(variable_bit[1])
                    num2 = int(variable_bit[3])
                    result = abs(num1 - num2) + 1
                    self.variable_bits[variable_name] = result
        for line_number, operation in enumerate(verilog_code, start=1):
            matches = re.findall(overflow_pattern, operation)

            for match in matches:
                signal = match[0]
                op1 = match[1]
                operator = match[2]
                op2 = match[3]
                
                # Check for overflow condition and add error if necessary
                if operator  == '+' and self.variable_bits[signal] <= max(self.variable_bits[op1], selfvariable_bits[op2]):
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may overflow."))
                elif operator == '-' and self.variable_bits[signal] < max(self.variable_bits[op1], self.variable_bits[op2]):
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may overflow."))
                elif operator == '*' and self.variable_bits[signal] < self.variable_bits[op1] + self.variable_bits[op2]:
                    self.errors['Arithmetic Overflow'].append((line_number, f"Signal '{signal}' may cause multiplication overflow."))
                elif operator == '/' and self.variable_bits[signal] < self.variable_bits[op1]:
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


    def check_inferred_latches(self, verilog_code):
        verilog_code_str = ''.join(verilog_code)
        lines = verilog_code_str.splitlines()

        for line_number, line in enumerate(lines, start=1):
            if re.search(r'\balways\s+@', line):
                always_block = self.extract_always_block(lines, line_number)
                #print(always_block)

                if re.search(r'\bif\b', always_block):
                    if not self.has_else_branch(always_block):
                        self.errors['Inferred Latches'].append(
                            (line_number, "Inferred latch found: 'if' statement without an 'else' branch."))

                if re.search(r'\bcase\b', always_block):
                    if not (self.complete_case(always_block)):
                        if not (self.has_default_case(always_block)):
                            self.errors['Inferred Latches'].append(
                                (line_number, "Inferred latch found: 'case' statement without a default case."))


    def has_else_branch(self, always_block):
        if_match = re.findall(r'\bif\s*\([^)]+\)', always_block)

        for if_statement in if_match:
            if re.search(r'else', if_statement):
                return True

        return False

    def complete_case(self, always_block):
        print("hello")
        case_pattern = r'\bcase\b'
        endcase_pattern = r'\bendcase\b'
        case_values_pattern = r'\bcase\s*\((.*?)\)'
        print("hello")

        case_positions = [match.start() for match in re.finditer(case_pattern, always_block)]
        endcase_positions = [match.start() for match in re.finditer(endcase_pattern, always_block)]

        for case_pos in case_positions:
            endcase_pos = next(pos for pos in endcase_positions if pos > case_pos)
            case_body = always_block[case_pos:endcase_pos]

        
            case_values_match = re.search(case_values_pattern, case_body)
            if case_values_match:
                case_values_str = case_values_match.group(1)
                # Extract values inside parentheses
                values = [value.strip() for value in case_values_str.split(',')]

                # Check if all possible combinations are covered
                num_bits = max[(len(value) for value in values)]
                expected_num_values = 2 ** num_bits
                covered_values = [value.split(':')[-1].strip() for value in values]
                
                if set(len(covered_values)) != expected_num_values:
                    return False

        return True

        

    def has_default_case(self, always_block):
        case_match = re.search(r'\bcase\s*\([^)]+\)', always_block)
        if case_match:
            case_block = always_block[case_match.end():]
            return re.search(r'\bdefault\b', case_block)

        return True












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
