import argparse
import os
import re
from pathlib import Path
import spacy
from commonregex import CommonRegex
import sys
import warnings
import en_core_web_md
import glob
warnings.filterwarnings('ignore')
nlp = spacy.load("en_core_web_md")


block = '\u2588'

def names(data):
    name_list = []
    doc = nlp(data)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            name = ent.text
            if name not in name_list:
                name_list.append(name)
    return data, name_list

def dates(data):
    parsed_text = CommonRegex(data)
    dates_list = parsed_text.dates
    return data, dates_list

def addresses(data):
    st_address = []
    loc_list = []
    parsed_text = CommonRegex(data)
    st_address = parsed_text.street_addresses
    doc = nlp(data)
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            loc = ent.text
            if loc not in loc_list:
                loc_list.append(loc)
    loc_list.extend(st_address)
    return data, loc_list

def phones(data):
    parsed_text = CommonRegex(data)
    phones_list = parsed_text.phones
    return data, phones_list


# def redact(data, names_list=None, dates_list=None, address_list=None, phones_list=None):
#     # Combine all lists into a single list for processing
#     all_entities = names_list + dates_list + address_list + phones_list
    
#     # Sort entities by length in descending order to avoid partial replacement issues
#     all_entities = sorted(all_entities, key=len, reverse=True)
    
#     # Escape entities to be used in a regular expression
#     all_entities = [re.escape(entity) for entity in all_entities]

#     for entity in all_entities:
#         # Replace each entity with the block character repeated for the length of the entity
#         data = re.sub(entity, block * len(entity), data)

#     return data
def redact(data, names_list=None, dates_list=None, address_list=None, phones_list=None):
    # Initialize statistics dictionary
    stats = {
        'names': {'count': 0, 'positions': []},
        'dates': {'count': 0, 'positions': []},
        'addresses': {'count': 0, 'positions': []},
        'phones': {'count': 0, 'positions': []}
    }
    
    # Function to replace and update stats
    def replace_and_update_stats(entity, category):
        nonlocal data
        positions = [m.start() for m in re.finditer(re.escape(entity), data)]
        for pos in positions:
            stats[category]['positions'].append((pos, pos + len(entity)))
            data = data[:pos] + (block * len(entity)) + data[pos + len(entity):]
        stats[category]['count'] += len(positions)
    
    # Process each category
    for name in names_list:
        replace_and_update_stats(name, 'names')
    for date in dates_list:
        replace_and_update_stats(date, 'dates')
    for address in address_list:
        replace_and_update_stats(address, 'addresses')
    for phone in phones_list:
        replace_and_update_stats(phone, 'phones')

    return data, stats





def save_censored_file(original_path, data, output_folder, suffix=".censored"):
    # Extract the base name without extension and then append the suffix
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    new_filename = base_name + suffix
    
    # Construct the full path to the output file within the output folder
    output_path = os.path.join(output_folder, new_filename)

    try:
        # Ensure the output directory exists; create it if it does not
        os.makedirs(output_folder, exist_ok=True)

        # Write the redacted data to the new file
        with open(output_path, 'w', encoding="utf-8") as file:
            file.write(data)
        
    except Exception as e:
        # If there's an error, print it
        print(f"Failed to save censored file: {e}")


# def process_files(input_pattern, output_folder, redact_names_flag, redact_dates_flag, redact_phones_flag, redact_addresses_flag):
#     # Ensure the modified output folder exists
#     os.makedirs(output_folder, exist_ok=True)

#     for file_path in Path('.').glob(input_pattern):
#         print(f"Processing file: {file_path}")
#         with open(file_path, 'r', encoding="utf-8") as file:
#             data = file.read()

#         # Collect data to redact based on flags
#         names_list, dates_list, address_list, phones_list = [], [], [], []
#         if redact_names_flag:
#             _, names_list = names(data)
#         if redact_dates_flag:
#             _, dates_list = dates(data)
#         if redact_addresses_flag:
#             _, address_list = addresses(data)
#         if redact_phones_flag:
#             _, phones_list = phones(data)

#         # Apply redactions
#         censored_data = redact(data, names_list, dates_list, address_list, phones_list)

#         # Save the censored data
#         save_censored_file(file_path, censored_data, output_folder)
def process_files(input_pattern, output_folder, redact_names_flag, redact_dates_flag, redact_phones_flag, redact_addresses_flag, stats_output):
    # Ensure the modified output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    overall_stats = []

    for file_path in Path('.').glob(input_pattern):
        
        with open(file_path, 'r', encoding="utf-8") as file:
            data = file.read()

        names_list, dates_list, address_list, phones_list = [], [], [], []
        if redact_names_flag:
            _, names_list = names(data)
        if redact_dates_flag:
            _, dates_list = dates(data)
        if redact_addresses_flag:
            _, address_list = addresses(data)
        if redact_phones_flag:
            _, phones_list = phones(data)

        censored_data, file_stats = redact(data, names_list, dates_list, address_list, phones_list)
        overall_stats.append((file_path.name, file_stats))
        
        save_censored_file(file_path, censored_data, output_folder)

    # Output stats
    output_stats(overall_stats, stats_output)

def output_stats(stats, output):
    stats_data = ""
    for filename, stat in stats:
        stats_data += f"File: {filename}\n"
        for category, details in stat.items():
            stats_data += f"{category.capitalize()}: Count = {details['count']}, Positions = {details['positions']}\n"
        stats_data += "\n"
    
    if output == "stderr":
        print(stats_data, file=sys.stderr)
    elif output == "stdout":
        print(stats_data)
    else:
        with open(output, 'w', encoding="utf-8") as file:
            file.write(stats_data)




def main():
    parser = argparse.ArgumentParser(description='Process and redact sensitive information from text files.')
    parser.add_argument('--input', type=str, required=True, help='Glob pattern for input text files to be processed.')
    parser.add_argument('--names', action='store_true', help='Redact names.')
    parser.add_argument('--dates', action='store_true', help='Redact dates.')
    parser.add_argument('--phones', action='store_true', help='Redact phone numbers.')
    parser.add_argument('--address', action='store_true', help='Redact addresses.')
    parser.add_argument('--output', type=str, required=True, help='Output folder for censored files.')
    parser.add_argument('--stats', type=str, help='Statistics output, e.g., stderr.')

    args = parser.parse_args()

    # Modify the output directory to include a .censored suffix
    modified_output_folder = os.path.join(args.output, '.censored')
    
     # Process files according to the specified criteria
    process_files(args.input, modified_output_folder, args.names, args.dates, args.phones, args.address, args.stats)


if __name__ == "__main__":
    main()
