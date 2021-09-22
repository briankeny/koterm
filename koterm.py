#!usr/bin/env python
# koterm version 1.0.0
# Required modules
import socket
import sys
import os
import argparse
import colorama
import threading
import requests
import time
import re
from urllib.parse import urlparse
from queue import Queue

# import random

# coloring
def color(color=None):
    global R, G, B, Y, V, L, W
    if color == "off":
        print("\t Coloring  is disabled ")
        R = G = Y = B = V = L = W = ""
    else:
        R, G, Y, B, V, L, W = (
            "\033[91m,",
            "\033[92m",
            "\033[93m",
            "\033[94m",
            "\033[95m",
            "\033[96m",
            "\033[0m",
        )
    return (R, G, Y, B, V, L, W)


# art banner
def art():
    print(
        """ %s
               _         _                                            ---_ ......_-_--.                              
              | |       | |                                          (|\ /      / /|\  \             
              | | ____ _| |___   _  _  _ __  _ _                     /  /      ,  ---'  '                                
              | |/ /   \  |  _ \| |/\/| '_ \/_' |                   /  /     .           '                       %s
              | | <  O  | | |__/| |   | | | | | |            %s     _/  /     .    /,)     )                      
              |_|\_\___/\_\___| |_|   |_| |_| |_|                /  o     o   _,  /     /                               
                                                                 \           ,   /   / *)                                   
                                                                  \________.// ,   / _\ *)                                   
                                                                   \|    \|// . . __ _ \ *)                               
                                                                    .  . //  , .  ___ __\ *)                     %s    
                                                                     \`-|\_/ /  |_ _ _ _ _\*)                        
                                                                      '/'\__/  (*\ __ __ _ \*)                                                            
                                                                     /^|        (*\ _ __ _ _\*)                             
                                                                    /  \         (*\ __ _ _  \*)                                                        
              %s
              
                # Coded by Brian
        """
        % (G, W, B, G, G)
    )


# error messaging
def error_Handler(errmsg):
    print(f"\t Usage: python {sys.argv[0]} -h for help\n")
    print("%s\t [?] Error: %s %s\n" % (R, errmsg, W))
    sys.exit()


# parse arguments
def argument_handler():
    parser = argparse.ArgumentParser(" Koterm Subdomain Finder")
    parser.add_argument(
        "-d",
        "--domain",
        required=False,
        help='Pass in a domain with  -d  ie: "-d google.com" or --domain "yahoo.com" ',
    )
    parser.add_argument(
        "-t",
        "--target",
        required=False,
        help='Pass in a target with  -t  ie: "-t 192.10.10.1 " or --target "www.safaricom.com" ',
    )
    parser.add_argument(
        "-p",
        "--ports",
        nargs="?",
        required=False,
        help="Pass in a port  with -p flag ie . -p 20,80,91 or --port 20  or -p- 1,5023",
    )
    parser.add_argument(
        "-pr",
        "--portrange",
        dest="p_range",
        nargs="?",
        required=False,
        help="Scan a port range ie. -pr 1,500 or --portrange 1,1024",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="stat",
        type=str,
        default="en",
        required=False,
        help="Enable verbose mode -v :ie --verbose en or -v en",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="file_name",
        required=False,
        help="Pass in a file to save output  with -s ie . -s mydom.txt or --save subdomains.txt",
    )
    parser.add_argument(
        "-c",
        "--color",
        default="on",
        type=str,
        dest="color",
        required=False,
        help=" Disable coloring with -c ie . -c off or --color off",
    )
    parser.error = error_Handler
    return parser.parse_args()


# Simple google  Search
class Server:
    def __init__(self, domain="", verbose=True):
        self.domain = domain
        self.subdomains = []
        self.verbose = verbose
        self.proxies = {}

    # def proxies(self):
    #     path = os.getcwd()
    #     path_wd = os.path.join(path, "kotroot", "proxy")
    #     file = open(path_wd, "r")
    #     proxy = file.read()
    #     proxie = proxy.splitlines()
    #     keys = "https"
    #     key = "http"
    #     for proxy in proxie:
    #         proxy = random.choice(proxie)
    #         self.proxies[keys] = proxy
    #         self.proxies[key] = proxy
    #     return self.proxies

    def find_subdomains(self):
        querry = f"site:{self.domain}"
        if self.verbose:
            print("\t%s [-] Non agressive scan...%s" % (B, W))
        filter = re.compile("((http|https)+\S+\w)")
        url = f"https://google.com/search?q={querry}&btnG=Search&num=600&hl=en-US&biw=&bih=&gbv=1&start=1&filter=0"
        try:
            response = requests.get(url, timeout=5)
        except:
            pass
        else:
            if (
                "Our systems have detected unusual traffic from your computer network"
                in (response.text)
            ):
                print("\t%s [?] Google is now blocking our requests %s" % (R, W))
                time.sleep(6)
            else:
                subdomain = filter.findall(str(response.text))
                for s in subdomain:
                    s = list(s)
                    s = "".join(map(str, s))
                    s = urlparse(s).netloc
                    if not s in self.subdomains and self.domain in s:
                        if self.verbose:
                            print("%s\t [+] Found a subdomain %s %s %s" % (G, L, s, W))
                        self.subdomains.append(s)
            time.sleep(1)
        return self.subdomains


# Use google search engine for advanced search


class GoogleEngine:
    def __init__(self, domain="", names=[], verbose=True, file_name=None):
        self.domain = domain
        self.names = names
        self.subdomains = []
        self.timeout = 15
        self.MAX_DOMAINS = 100
        self.page = 1
        self.verbose = verbose
        self.resp = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8",
            "Accept-Encoding": "gzip",
        }
        print("%s\t [-] Searching now in Google...%s" % (G, W))
        if self.verbose:
            print("%s\t [-] Entering agressive scan...%s" % (B, W))

    def pause(self):
        time.sleep(5)
        return

    def querry(self):
        if self.names:
            fmt = "site:{domain} -www.{domain} -{found}"
            found = " -".join(self.names[: self.MAX_DOMAINS - 2])
            query = fmt.format(domain=self.domain, found=found)
        else:
            query = "site:{domain} -www.{domain}".format(domain=self.domain)
        return query

    def req(self):
        que = self.querry()
        url = f"https://google.com/search?q={que}&btnG=Search&num=150&hl=en-US&biw=&bih=&gbv=1&start={self.page}&filter=0"
        try:
            self.resp = requests.Session().get(
                url, headers=self.headers, timeout=self.timeout
            )
        except Exception:
            self.resp = None
            pass
        if self.resp is None:
            return 0
        if (
            "Our systems have detected unusual traffic from your computer network"
            in self.resp.text
        ):
            print("\t%s [+] Google is now blocking our requests  %s" % (R, W))
            self.pause()
        else:
            self.resp = (
                self.resp.text if hasattr(self.resp, "text") else self.resp.content
            )
        return self.resp

    def res(self):
        reg = re.compile('href="/url?\S+\w.\S?"')
        try:
            liks = reg.findall(self.resp)
            regx = re.compile(f"https://\S+[\w]\S?[{self.domain}]")
            links = regx.findall(str(liks))
            for link in links:
                link = urlparse(link).netloc
                if not link in self.subdomains and self.domain in link:
                    self.subdomains.append(link)
                    if self.verbose:
                        print("%s\t [+] Found a subdomain %s %s" % (G, L, link))

        except Exception:
            pass
        return self.subdomains

    def chain(self):
        while self.page <= 2:
            self.req()
            self.res()
            self.pause()
            self.page += 1
        return self.subdomains


# port scanner class
class PortScan:
    def __init__(self, domains=[], target="", ports=[], p_range=[], verbose=False):
        self.ports = ports
        self.target = target
        self.p_range = p_range
        self.domains = domains
        self.verbose = verbose
        self.silent = False
        self.count = 0
        self.basket = ""

    def portscan(self):
        if self.domains:
            print(
                "%s\t [-] Initiating a port scan for discovered subdomains... %s"
                % (Y, W)
            )
            for domain in self.domains:
                try:
                    ip_4 = socket.gethostbyname(domain)
                except:
                    if self.verbose:
                        print(
                            "%s\t [!] %s did not resolve to an ip address %s"
                            % (R, domain, W)
                        )
                    pass
        if self.target:
            print("%s\t [-] Initiating a port scan on %s%s" % (Y, self.target, W))
            try:
                ip_4 = socket.gethostbyname(self.target)
                if self.verbose:
                    print(
                        "%s\t [-] %s has an ip address of  %s  %s"
                        % (L, self.target, ip_4, W)
                    )
            except:
                print(
                    "%s\t [!] Oops sorry there was an error in resolving this name or ip address %s  %s"
                    % (R, self.target, W)
                )
                sys.exit()
        socket.setdefaulttimeout(0.55)

        def scan(self, port, ip_4):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            try:
                connection = sock.connect((ip_4, port))
                with threading.Lock():
                    if self.verbose:
                        print("\t%s [+] Port %s tcp open %s" % (G, port, W))
                    self.basket += port + ","
                self.count += 1
                connection.close()
            except:
                pass

        def threads(port, ip_4):
            while True:
                port = q.get()
                port = int(port)
                scan(self, port, ip_4)
                q.task_done()

        q = Queue()
        if self.ports != None and self.ports != []:
            for port in self.ports:
                threading.Thread(target=threads, daemon=True, args=(port, ip_4)).start()
                q.put(port)
        elif self.p_range != [] and self.p_range != None:
            self.p_range.sort()
            beg = int(self.p_range[0])
            end = int(self.p_range[-1])
            for port in range(beg, end):
                threading.Thread(target=threads, daemon=True, args=(port, ip_4)).start()
                q.put(port)
        else:
            for port in range(1, 500):
                threading.Thread(target=threads, daemon=True, args=(port, ip_4)).start()
                q.put(port)
        q.join()
        if self.verbose == False:
            print("%s\t [+]  Port status [open]%s : %s  %s" % (G, L, self.basket, W))
        print("%s\t [+] Discovered %d  ports  open %s" % (V, self.count, W))
        print("%s\t [+] Port scan complete  %s" % (Y, W))
        exit


def port_scanner(domains, target, ports, p_range, verbose):
    if ports != None:
        ports = ports.split(",")
    if p_range != None:
        p_ran = p_range.split(",")
        pran = []
        for p in p_ran:
            try:
                pran.append(int(p))
            except:
                sys.exit()
            p_range = p_ran
    scan = PortScan(domains, target, ports, p_range, verbose)
    action = scan.portscan()
    return action


# save subdomains to a file
def saved_Info(file_name, subdomains, verbose):
    if verbose == True:
        print("%s\t [-] Saving found subdomains to file %s " % (W, file_name))
    with open(str(file_name), "wt") as f:
        for subdomain in subdomains:
            f.write("\n%s" % subdomain)


def finder(domain, verbose):
    print(
        "%s\t [!] Finishing the search this may take longer please wait...%s" % (W, W)
    )
    subdomains = []
    next_ = []
    path = os.getcwd()
    pa_wd = os.path.join(path, "kotroot", "final")
    file = open(pa_wd, "r")
    final_ = file.read()
    file.close()
    names = final_.splitlines()
    for s in names:
        if not s == "":
            s = s.strip()
            url = f"http://{s}.{domain}"
            next_.append(url)
    for url in next_:
        try:
            resp = requests.get(url, timeout=0.95)
        except:
            pass
        else:
            url = urlparse(url).netloc
            if verbose:
                print("\t%s [+] Found a subdomain %s %s %s" % (G, L, url, W))
                subdomains.append(url)
    print("\t%s [-] Search is now  complete %s" % (B, W))
    return subdomains


def order(domain, target, p_range, file_name, ports, verbose):
    if target != None:
        port_scanner(
            domains=None, target=target, ports=ports, p_range=p_range, verbose=verbose
        )
        sys.exit()
    if domain:
        print("%s\t [-] Beggining search  for subdomains for %s %s" % (Y, domain, W))
        final_list = set()
        path = os.getcwd()

        path_wd = os.path.join(path, "kotroot", "wordlist")
        file_2 = open(path_wd, "r")
        fl = file_2.read()
        wrds = fl.splitlines()
        file_2.close()
        names = list(n.strip() for n in wrds if n != "")

        google = GoogleEngine(domain, names, verbose, file_name)
        subdomains_1 = google.chain()

        server = Server(domain, verbose)
        subdomains_2 = server.find_subdomains()
        subdomains_3 = finder(domain, verbose)

        if subdomains_1 != [] or subdomains_2 != [] or subdomains_3 != []:
            subdomains = list(
                final_list.union(subdomains_2, subdomains_1, subdomains_3)
            )
        else:
            subdomains = []
        if file_name:
            saved_Info(file_name, subdomains, verbose)
        if ports or p_range:
            domains = subdomains
            port_scanner(domains, target, ports, p_range, verbose)
    print("%s\t [+] Total discovered subdomains %s%s" % (V, len(subdomains), W))
    print("%s\t [-] Search ends here %s" % (Y, W))
    return


# putting  code all together
def main():
    args = argument_handler()
    domain = args.domain
    ports = args.ports
    target = args.target
    file_name = args.file_name
    verbose = args.stat
    p_range = args.p_range
    if verbose == "en":
        verbose = True
    elif verbose == "dis" or verbose == "off" or verbose == "Off":
        verbose = False
    else:
        verbose = False
    col = args.color
    if sys.platform.startswith("win"):
        colorama.init()
    color(col)
    art()
    if not (domain or target):
        error_Handler("Missing arguments :- target or a domain")
    else:
        order(domain, target, p_range, file_name, ports, verbose=verbose)


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")
    main()
