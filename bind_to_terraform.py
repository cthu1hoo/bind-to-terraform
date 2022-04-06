#!/usr/bin/python3

# based on https://download.huihoo.com/google/gdgdevkit/DVD1/developers.google.com/cloud-dns/migrating-bind-zone-python.html
# for the time being only supports A, MX, and CNAME record types.

import dns.zone
from dns.zone import NoSOA
from dns.exception import DNSException
from dns.rdataclass import *
from dns.rdatatype import *
from dns import rdatatype

import sys

tpl_dns_a_record_set = '''
# terraform import dns_a_record_set.{name} {name}.{domain}.
resource "dns_a_record_set" "{name}" {{
    addresses = [
        {addresses}
    ]
    name      = "{name}"
    ttl       = {ttl}
    zone      = "{domain}."
}}
'''

tpl_dns_cname_record = '''
# terraform import dns_cname_record.{name} {name}.{domain}.
resource "dns_cname_record" "{name}" {{
    cname     = "{cname}."
    name      = "{name}"
    ttl       = {ttl}
    zone      = "{domain}."
}}
'''

tpl_dns_txt_record_set = '''
# terraform import dns_txt_record_set.{name} {name}.{domain}.
resource "dns_txt_record_set" "{name}" {{
    name = "{name}"
    txt = [
        {strings}
    ]
    ttl = {ttl}
    zone = "{domain}."
}}
'''

def canonicalize(name, domain):
    if domain not in name:
        return name + "." + domain
    else:
        return name

def parse_zone(zone_file, domain):
    out = ""

    zone = dns.zone.from_file(zone_file, domain)
    for name, node in zone.nodes.items():
        if str(name) in ["@", "*"] or "." in(str(name)):
            continue

        rdatasets = node.rdatasets
        for rdataset in rdatasets:

            if rdataset.rdtype == TXT:
                strings = []

                for rdata in rdataset:
                    strings.append('"' + rdata.strings[0].decode("utf-8") + '"')

                out += tpl_dns_txt_record_set.format(
                    name=name,
                    strings=', '.join(strings),
                    ttl=rdataset.ttl,
                    domain=domain)

            elif rdataset.rdtype == CNAME:
                for rdata in rdataset:
                    out += tpl_dns_cname_record.format(
                        name=name,
                        cname=canonicalize(str(rdata.target), domain),
                        ttl=rdataset.ttl,
                        domain=domain)
            elif rdataset.rdtype == A:
                addresses = []

                for rdata in rdataset:
                    addresses.append(f"\"{rdata.address}\"")

                out += tpl_dns_a_record_set.format(
                    name=name,
                    addresses=', '.join(addresses),
                    ttl=rdataset.ttl,
                    domain=domain)
    return out

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} ZONEFILE DOMAIN")
    else:
        out = parse_zone(sys.argv[1], sys.argv[2])
        print(out)