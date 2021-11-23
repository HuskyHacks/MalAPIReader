import pefile
import requests
import bs4
import argparse
import sys
import os
from utils.colors import *
import datetime

parser = argparse.ArgumentParser(description="Read information from MalAPI.io for WinAPI information.")
parser.add_argument("--pe", "-p",
                    help="Specify a PE to read. The WinAPI will be checked against MalAPI and information will be "
                         "printed about the API if the information is present.")
parser.add_argument("--look", "-l", help="Look up an API by name and print all information.")
parser.add_argument("--verbose", "-v", help="Increase verbosity of output", action="store_true")
args = parser.parse_args()
if len(sys.argv) == 1:
    parser.print_help()
    parser.exit()

# Globals
current_time = datetime.datetime.now()


def check_api(api):
    sus_api = {}
    APItoCheck = api
    if args.verbose:
        print(info + APItoCheck)
    APICheck = requests.get("https://malapi.io/winapi/" + APItoCheck)
    APICheck.raise_for_status()
    APISoup = bs4.BeautifulSoup(APICheck.text, 'html.parser')
    details = APISoup.select('.detail-container .content')
    ApiInfo = details[1].getText().lstrip().rstrip()
    if ApiInfo != "":
        print(important + api)
        sus_api[api] = ApiInfo
        return sus_api
    else:
        return


def api_lookup():
    # Lookpup an individual API by name
    global mal_apis
    if (args.look):
        check_api(args.look)
    # Read read import table from PE and print information when it is found.
    elif (args.pe):
        pe = pefile.PE(args.pe, fast_load=True)
        pe.parse_data_directories()
        mal_apis = {}
        try:
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                if args.verbose:
                    print("----", entry.dll.decode("utf-8"), "----")
                for imp in entry.imports:
                    try:
                        malicious = check_api(imp.name.decode("utf-8"))
                        mal_apis.update(malicious)
                    except:
                        continue
        except KeyboardInterrupt:
            pass
    return mal_apis


def print_results(mal_apis):
    print("")
    print("-" * 15 + "RESULTS" + "-" * 15)
    print("")

    print(info + "Time: " + str(current_time))
    print(info + "Sample: " + args.pe + "\n")

    for x in mal_apis.keys():
        print(important + str(x) + "\n    \\\\---> " + str(mal_apis[x]))

    print("\n\nIf a WINAPI listed here was used maliciously, but no description was given, consider contributing "
          "information to https://malapi.io.")


def main():
    mal_api_results = api_lookup()
    print_results(mal_api_results)


if __name__ == "__main__":
    main()
