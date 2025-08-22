import argparse
from .main import virtual_assistant

def main():
    parser = argparse.ArgumentParser(description="ELSA Virtual Assistant CLI")
    parser.add_argument('--start', action='store_true', help='Start the ELSA virtual assistant')
    args = parser.parse_args()

    if args.start:
        virtual_assistant()
    else:
        parser.print_help()
