import bang
import argparse
from bn_to_assa import convert

parser = argparse.ArgumentParser()
parser.add_argument('-f')
parser.add_argument('--type')

args = parser.parse_args()

f = args.f
t = args.type

if t == 'bnet':
    f = convert(f)

pbn = bang.load_from_file(f, "assa")
pbn._n_parallel = max(77, pbn.n_nodes ** 4)
pbn.device = "cpu"

attractors = pbn.monte_carlo_detect_attractors(trajectory_length=1100, attractor_length=1300)
print(len(attractors))
