from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *

class VerilogLintVisitor(NodeVisitor):
    def __init__(self):
        self.violations = []

    def visitAssign(self, assign_node):
        # Check for Un-initialized Register
        if assign_node.right is None:
            self.violations.append({
                'check_name': 'Un-initialized Register',
                'line_number': assign_node.lineno,
                'target_signal': assign_node.left.var.name,
            })
            
    def visitAlways(self, always_node):
        # Check for Unreachable Blocks
        if not always_node.statement:
            self.violations.append({
                'check_name': 'Unreachable Blocks',
                'line_number': always_node.lineno,
            })
            
          # Check for Infer Latch
        if isinstance(always_node.statement, list) and len(always_node.statement) == 1:
            stmt = always_node.statement[0]
            if not isinstance(stmt, (Assign, If, Case)):
                self.violations.append({
                    'check_name': 'Infer Latch',
                    'line_number': always_node.lineno,
                })
                
    def visitCase(self, case_node):
        # Check for Non Full/Parallel Case
        if not all(isinstance(cond, (Assign, If)) for cond in case_node.cond):
            self.violations.append({
                'check_name': 'Non Full/Parallel Case',
                'line_number': case_node.lineno,
            })
    
    def visitIf(self, if_node):
        # Check for Unreachable FSM State
        if not if_node.thenstatement and not if_node.elsestatement:
            self.violations.append({
                'check_name': 'Unreachable FSM State',
                'line_number': if_node.lineno,
            })
            
    def is_signed_integer(self, node):
        return isinstance(node, IntConst) and node.value.startswith('-')

    def detect_arithmetic_overflow(self, binop_node):
        if binop_node.op in ('+', '-', '*', '/'):
            left_value = int(binop_node.left.value)
            right_value = int(binop_node.right.value)

            if binop_node.op == '+':
                result = left_value + right_value
            elif binop_node.op == '-':
                result = left_value - right_value
            elif binop_node.op == '*':
                result = left_value * right_value
            elif binop_node.op == '/':
                if right_value == 0:
                    return  # Division by zero, avoid potential division error
                result = left_value / right_value

            if result > (2**31 - 1) or result < -(2**31):
                self.violations.append({
                    'check_name': 'Arithmetic Overflow',
                    'line_number': binop_node.lineno,
                })

    def visitBinOp(self, binop_node):
        # Check for Arithmetic Overflow
        self.detect_arithmetic_overflow(binop_node)
    
    def visitModuleDef(self, moddef_node):
        # Check for Multi-Driven Bus/Register
        driven_signals = set()
        for always_node in moddef_node.children():
            if isinstance(always_node, Always):
                for stmt in always_node.statement:
                    if isinstance(stmt, Assign):
                        target_signal = stmt.left.var.name
                        if target_signal in driven_signals:
                            self.violations.append({
                                'check_name': 'Multi-Driven Bus/Register',
                                'line_number': stmt.lineno,
                                'target_signal': target_signal,
                            })
                        else:
                            driven_signals.add(target_signal)
                            
def lint_verilog(verilog_code):
    ast = parse(verilog_code)
    lint_visitor = VerilogLintVisitor()
    lint_visitor.visit(ast)
    return lint_visitor.violations
       
def generate_report(violations, output_file="lint_report.txt"):
    # Open the text file for writing
    with open(output_file, 'w') as file:
        # Generate a report with the linting results and write to the file
        for violation in violations:
            file.write(f"Check Name: {violation['check_name']}\n")
            file.write(f"Line Number: {violation['line_number']}\n")
            if 'target_signal' in violation:
                file.write(f"Target Signal: {violation['target_signal']}\n")
            file.write('-' * 30 + '\n')
        
def main():
    # Read Verilog code from a file
    with open('your_verilog_file.v', 'r') as file:
        verilog_code = file.read()

    # Perform linting
    violations = lint_verilog(verilog_code)

    # Generate a report
    generate_report(violations)
    
if __name__ == "__main__":
    main()
    