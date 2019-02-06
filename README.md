# Mini Project: Network Security
By Shahar Bashari, Ben Gurion University, Sem A 2019


## Usage:
```
$ sudo arp_poison.py -v <victim_ip> -g <gateway_ip>
Change hosts.txt to your liking and add resources to /var/www/html
$ sudo dns_spoof.py -f <hosts_file_location> -i <interface>
$ service apache2 start 
```

## Installation:
* Download Python 2.7
* Download scapy, dropbox and auto-py-to-exe modules:
```
$ pip install pyx==0.12.1 matplotlib cryptography ipython scapy dropbox auto-py-to-exe
```

## Author:

Shahar Bashari

## Disclaimer:

The scripts are used for educational purposes only, not to attack real life people.
