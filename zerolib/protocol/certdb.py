from collections import namedtuple
from random import SystemRandom
from pathlib import Path

Fields = namedtuple('Fields', ['country', 'state', 'locality', 'org', 'unit', 'common', 'delta', 'dns_names'])


def make_fields():
    dirname = str(Path(__file__).parent.absolute())
    variables = ('country', 'state','locality', 'org', 'common', 'dns')

    for var in variables:
        var_name = 'list_' + var
        if not globals()[var_name]:
            with open(dirname + '/data/' + var + '.list', 'r', encoding='utf-8') as f:
                globals()[var_name] = [line.strip() for line in f]

    global default_fields
    if not default_fields:
        with open(dirname + '/data/default.yaml', 'r', encoding='utf-8') as f:
            parser = yaml_parser(f)
            default_fields = list(parser)

    return real_make_fields()

def real_make_fields():
    rng = SystemRandom()

    field_id = rng.randint(-len(default_fields), len(default_fields) - 1)
    if field_id >= 0:
        return default_fields[field_id]

    country = rng.choice(list_country)
    state = rng.choice(list_state)
    locality = rng.choice(list_locality)
    org = ''
    unit = ''

    org_cond = rng.randint(0, 3)
    if org_cond == 1:
        org = rng.choice(list_org)
    elif org_cond == 2:
        unit = rng.choice(list_org)
    elif org_cond == 3:
        org = rng.choice(list_org)
        unit = rng.choice(list_org)

    common = rng.choice(list_common)
    delta = rng.choice(list_delta)

    dns_set = set()
    dns_count = max(0, rng.randint(-7, 7))
    for i in range(dns_count):
        dns_set.add(rng.choice(list_dns))
    if (not dns_set) or rng.randint(0, 5):
        dns_set.add('localhost')
    dns_names = sorted(dns_set)

    return Fields(
        country=country,
        state=state,
        locality=locality,
        org=org,
        unit=unit,
        common=common,
        delta=delta,
        dns_names=dns_names,
    )

##############################################################################

def field_parser(d):
    if d:
        delta = int(d['delta'])
        dns_names = sorted((n for n in d['dns_names'].split(' ') if n))
        yield Fields(
            country=d['country'],
            state=d['state'],
            locality=d['locality'],
            org=d['org'],
            unit=d['unit'],
            common=d['common'],
            delta=delta,
            dns_names=dns_names)

def yaml_parser(f):
    yaml_dict = {}
    for line in f:
        line = line.strip()
        if line.startswith('-'):
            yield from field_parser(yaml_dict)
            yaml_dict = {}
        else:
            i = line.find(':')
            if i > 0:
                key, value = line[0:i].strip(), line[i+1:].strip()
                yaml_dict[key] = value

    yield from field_parser(yaml_dict)

default_fields = None

list_country = None
list_state = None
list_locality = None
list_org = None
list_common = None
list_dns = None

list_delta = (
    10, 15, 28, 29, 30, 31, 60, 90, 100, 120,
    360, 365, 365*2, 365*3, 3600, 3650,
)
