import ast
import csv
import json
import sys


def args_to_json(argv):
    # Create a dictionary to hold arguments
    # Skip the first element argv[0] as it is the script name
    arg_dict = {f"arg{i}": arg for i, arg in enumerate(argv[1:], 1)}
    return json.dumps(arg_dict, indent=4)


def args_to_dict(args):
    arg_dict = {}
    for arg in args:
        if ':' in arg:
            key, value = arg.split(':')
            arg_dict[key] = value
    return arg_dict



if __name__ == "__main__":
    # input_argv = sys.argv[1:]
    
    # input_arg = '"color":"hi"'
    # print(type(input_argv))
    # print(input_argv)

    # print(type(input_arg))
    # print(input_arg)
    # parsed_dict = json.loads(f'{{{input_arg}}}')
    # print(type(parsed_dict))
    # print(parsed_dict)
    # Remove the script name (first argument) from sys.argv
    # command_line_args = sys.argv[1:]
    # actual_str = str(command_line_args)
    # # actual_str = '{"color": "White", "level": "4", "variant": "Standard", "clock_limit": "10", "clock_increment": "5"}'
    # actual_str = actual_str[:0] + actual_str[1:-3] 
    # actual_str = list(actual_str.split(","))
    # for i in range(len(actual_str)):
    #     actual_str[i] = actual_str[i].replace('"', '')
    # # Convert command-line arguments to a dictionary
    # arguments_dict = args_to_dict(actual_str)
    input_argv = sys.argv[1:]
    s = str(input_argv)
    s = s[2:-2]
    r = s.replace("'", '"')
    j = json.loads(r)

    with open('testyText.csv', 'w') as file:
        file.truncate(0)
    print(f"Contents of {'testyText.csv'} have been deleted.")

    with open('testyText.csv', 'a', newline='') as file:
            writer = csv.writer(file) 
            writer.writerow([j['level']])
    print("hello in testy!")