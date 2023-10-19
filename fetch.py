import requests
import json
import argparse
import urllib3
from colorama import Fore
import time
import sys

#ADD YOUR API KEY HERE
api_key = ""

urllib3.disable_warnings()
def fetch_apex_domains(domain, size=1000, scope_limit = 1000000):

    all_results = []  # Initialize an empty list for all results
    scope_limit = int(scope_limit)
    base_url = "https://urlscan.io/api/v1/search/"
    search_after = None
    total_fetched = 0
    total = None
    api_header = {"API-Key": api_key}

    while total is None or total_fetched < total and total_fetched <= scope_limit:

        params = {
            "q": f"page.domain:{domain}",
            "size": size,
        }
        if search_after:
            params["search_after"] = search_after

        response = requests.get(base_url,verify=False , params=params, headers=api_header)
        data = response.json()

        if total is None:
            total = data.get("total")

        results = data.get("results", [])
        all_results.extend(results)

        if len(results) > 0:
            search_after = ','.join(map(str, results[-1].get("sort")))
        else:
            break

        total_fetched += len(results)

        print(f"[+]Fetched {total_fetched} out of {total}")
        
    return all_results

def write_results_to_file(results, filename, directory):
    with open(directory + filename, 'w') as f:
        json.dump(results, f)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Urlscan.io grab results - Moopinger')
    parser.add_argument('-domain', type=str, help='(-d) Domain to fetch urlscan results for eg. test.com')
    parser.add_argument('-file', type=str, help='(-f) Files containing domains to fetch')
    parser.add_argument('-output', type=str, default="./", help="(-o) Directory to place json results file (default is working dir)")
    args = parser.parse_args()


    targets = []
    lines = []
    counter=0
    directory = args.output


    if args.domain is None and args.file is None:
        parser.print_help()
        sys.exit(1)

    if args.domain:
        targets.append(args.domain)

    elif args.file:
        print("Reading domains from file...")
        with open(args.file, 'r') as file:
            targets = file.readlines()


    total_ents = len(targets)


    for domain_to_search in targets:
            domain_to_search = domain_to_search.strip()
            print(f"Starting against {domain_to_search} : [{counter+1} / {total_ents}] ")
            scope_limit = 1000000 #Hard limit the number of returned values for testing
            all_results = fetch_apex_domains(domain_to_search, 500, scope_limit)
            output_file = domain_to_search.replace(".","_") + "_all_results.json"
            write_results_to_file(all_results, output_file, directory)

            counter += 1
            time.sleep(2)







