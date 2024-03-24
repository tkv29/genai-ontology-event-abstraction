import argparse
from journey_tools.patient_journey_generator import generate_patient_journey
# from journey_tools.journey_to_xes_converter import convert_journey_to_xes

parser = argparse.ArgumentParser(description="Patient Journey to XES Converter")
subparsers = parser.add_subparsers(dest="command")

# Define sub-parser for creating patient journeys
create_parser = subparsers.add_parser("create", help="Create and save random generated patient journeys in the directory's result/patient_journeys/generated_patient_journeys folder")

# Define sub-parser for converting patient journeys to XES
# convert_parser = subparsers.add_parser("convert", help="Convert patient journeys to XES event log")
# convert_parser.add_argument("journey_files", nargs="+", help="List of patient journey files")
# convert_parser.add_argument("output_xes", help="Output XES file path")

args = parser.parse_args()

if args.command == "create":
    generate_patient_journey()
# elif args.command == "convert":
#     convert_journey_to_xes(args.journey_files, args.output_xes)