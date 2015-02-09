import argparse
import os
from abc import ABCMeta, abstractproperty

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--destination", dest = "destination_folder", default = ".",
                        help = "destination folder for output file (default: current folder)")
    parser.add_argument("-f", "--format", dest = "format", choices=["cnf", "lpx"], default = "cnf",
                        help ="format of output file (default: cnf)")
    parser.add_argument("input_file", help="input file in dimacs format which needs to be converted to specified format")
    return parser.parse_args()

class Converter:
    __metaclass__ = ABCMeta

    @abstractproperty
    def extension(self):
        pass

    @abstractproperty
    def generate_start_lines(self, line):
        pass

    @abstractproperty
    def generate_middle_line(self, line, i):
        pass

    def generate_end_lines(self):
        return ""

    def read_first_line(self, line):
        data = line.split()
        print "Total Number of Vertices = " + data[2]
        print "Total Number of Vertices = " + data[3]
        self.total_vertices = int(data[2])
        self.total_edges = int(data[3])

    def convert(self, input, output):
        print "\nInput file: " + input
        print "\nPerforming the conversion......"
        print "Location of output file: " + output
        with open(output, 'w') as o_stream:
            with open(input, "r") as in_stream:
                i = 0
                for line in in_stream:
                    if line.strip().startswith("c"):
                        continue

                    if i == 0:
                        self.read_first_line(line)
                        o_stream.write(self.generate_start_lines(line))
                    else:
                        o_stream.write(self.generate_middle_line(line, i))

                    i = i + 1
                o_stream.write(self.generate_end_lines())
        print "\nOutput file successfully generated."

class CNFConverter(Converter):
    def extension(self):
        return ".cnf"

    def generate_start_lines(self, line):
        return line.replace("edge", "cnf")

    def generate_middle_line(self, line, i):
        return line.replace("e", "").strip() + ' 0\n'

class LPXConverter(Converter):
    def extension(self):
        return ".lpx"

    def generate_start_lines(self, line):
        start_lines = "Min\n  obj:"
        for x in range(self.total_vertices):
            if (x != 0) and ((x % 20) == 0):
                start_lines = start_lines + "\n    "

            start_lines = start_lines + " +x" + str(x + 1)

        start_lines = start_lines + "\nst\n"
        return start_lines

    def generate_middle_line(self, line, i):
        edge = line.replace("e", "").strip().split()
        return "  c" + str(i) + ": +x" + edge[0] + " +x" + edge[1] + " >= 1\n"

    def generate_end_lines(self):
        end_lines = "Binary\n  "
        for x in range(self.total_vertices):
            if (x != 0) and ((x % 20) == 0):
                end_lines = end_lines + "\n    "  #move over to next line

            end_lines = end_lines + " x" + str(x + 1)

        end_lines = end_lines + "\nEND"
        return end_lines

if __name__ == '__main__':
    args = parse_arguments()

    if (args.format == "lpx"):
        converter = LPXConverter()
    else:
        converter = CNFConverter()

    input = args.input_file
    filename = os.path.splitext(os.path.basename(input))
    output = os.path.join(args.destination_folder, filename[0] + converter.extension())

    converter.convert(input, output)