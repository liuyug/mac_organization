#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import json
import csv
import argparse
import logging

logger = logging.getLogger(__name__)


def load_mac_file(oui_file):
    def parse_group(line_no, group_no, group_items):
        items = group_items[0].split('\t')
        mac_hex = items[0].split(' ')[0]
        company = items[-1].strip()
        items = group_items[1].split('\t')
        mac_base16 = items[0].split(' ')[0]
        company2 = items[-1].strip()
        assert company == company2
        if len(group_items) > 2:
            address = group_items[2].strip()
            address2 = group_items[3].strip()
            country = group_items[4].strip()
        else:
            address = None
            address2 = None
            country = None
        return {
            'hex': mac_hex,
            'base16': mac_base16,
            'company': company,
            # 'company2': company2,
            'address': address,
            'address2': address2,
            'country': country,
        }

    mac_orgs = []
    with open(oui_file) as f:
        line_no = 1
        group_no = 0
        group_items = []
        for line in f.readlines():
            line_no += 1
            if not line or line == '\n':
                if group_no == 0:
                    # header
                    pass
                else:
                    group = parse_group(line_no, group_no, group_items)
                    mac_orgs.append(group)
                    print(f'{group_no:03d} {line_no:03d} {group["hex"]} {group["company"]}')
                group_no += 1
                group_items = []
            else:
                group_items.append(line)
        if group_items:
            group = parse_group(line_no, group_no, group_items)
            mac_orgs.append(group)
            print(f'{group_no:03d} {line_no:03d} {group["hex"]} {group["company"]}')

    return mac_orgs


def output(mac_orgs, csv_file=None, json_file=None):
    if json_file:
        json.dump(mac_orgs, open(json_file, 'w'))
        print(f'Output {json_file}')
    if csv_file:
        with open(csv_file, 'w', newline='') as f_csv:
            header = ['hex', 'base16', 'company', 'address', 'address2', 'country']
            writer = csv.DictWriter(f_csv, fieldnames=header)
            writer.writeheader()
            writer.writerows(mac_orgs)
        print(f'Output {csv_file}')


def main():
    name = 'app'
    version = '1.0.0'
    description = 'Application Description'
    about = f'{name} v{version} {description}'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--version', action='version', version=about,
                        help='show version')
    parser.add_argument('-v', '--verbose', action='count',
                        default=0, help='verbose output')

    group = parser.add_argument_group('group')
    group.add_argument('--input', help='input oui file')
    group.add_argument('--json', help='output json')
    group.add_argument('--csv', help='output csv')

    args = parser.parse_args()
    # log to stdout in cli mode
    level = logging.INFO - args.verbose * 10
    logging.basicConfig(
        level=level,
        format='%(message)s',
    )

    if args.input:
        oui_file = args.input
        mac_orgs = load_mac_file(oui_file)
        if args.json:
            output(mac_orgs, json_file=args.json)
        if args.csv:
            output(mac_orgs, csv_file=args.csv)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
