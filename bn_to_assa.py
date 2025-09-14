import argparse
from jinja2 import Environment, FileSystemLoader, select_autoescape
import re


def convert(fp):
    env = Environment(loader=FileSystemLoader("."))

    tpl = env.get_template("assa_template.jj2")

    target = set()
    factors = set()
    funcs = {}

    with open(fp, 'r') as f:
        next(f)
        for i, og_line in enumerate(f):
            if len(og_line) == 0:
                continue
            og_line = re.sub(r"\s+", "", og_line)
            line = og_line.split(',')
            if len(line) < 2:
                continue
            # print(line)
            funcs[line[0]] = line[1].replace('~', '!')
            target.add(line[0])
            line = line[1]
            line = line.replace('(', ' ')
            line = line.replace(')', ' ')
            line = line.replace('!', ' ')
            line = line.replace('~', ' ')
            line = line.replace('&', ' ')
            line = line.replace('|', ' ')
            line = line.split()
            # print(line)
            for g in line:
                factors.add(g)

        for x in factors - target:
            funcs[x] = f"{x}\n"

    # for i in funcs.keys():
    #     print(i, funcs[i])

    # print(len(funcs))

    model = tpl.render(log_funcs=funcs, n=len(funcs))

    with open(f"{fp[:-5]}.assa", 'w+') as f:
        f.writelines(model)

    return f"{fp[:-5]}.assa"


if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument('-f', type=str)

    args = parse.parse_args()
    fp = args.f
    convert(fp)
