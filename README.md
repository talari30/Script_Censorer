# cis6930sp24-assignment1

README for Censoror Script

Overview:-
The Censoror script is designed to redact sensitive information from text files, including names, dates, phone numbers, and addresses. Utilizing the power of spaCy and regular expressions, it processes files to identify and censor specified types of data, offering customization through command-line arguments. The script also collects and outputs statistics about the redaction process, such as the types and counts of censored terms.

Features:-
Text Redaction: Automatically redacts names, dates, addresses, and phone numbers from text files.
Customizable Output: Saves redacted files with a .censored suffix in a specified output directory.
Statistics Generation: Provides detailed statistics about each redaction, including counts and positions of censored items.

Dependencies:-
Python 3.6+
spaCy
en_core_web_md (spaCy model)
CommonRegex

Installation:-

Install Python 3.6+ if not already installed.
Install required packages:-
pipenv install
pipenv install spacy commonregex
python -m spacy download en_core_web_md

Usage
Run the script from the command line, specifying the input files and options:-
pipenv run python censoror.py --input '*.txt' \
                    --names --dates --phones --address\
                    --output 'files/' \
                    --stats stderr

Command-Line Arguments:-
--input: Glob pattern for input text files to be processed.
--names: Flag to redact names.
--dates: Flag to redact dates.
--phones: Flag to redact phone numbers.
--address: Flag to redact addresses.
--output: Output folder for censored files.
--stats: Output for statistics (stdout, stderr, or filename).

Functions
names(data):-
Identifies and collects names from the provided text data using spaCy's named entity recognition.

Parameters:

data: The text data to process.
Returns:
A tuple of the original data and a list of identified names.

dates(data):-
Finds dates in the text data using CommonRegex.

Parameters:

data: The text data to process.
Returns:
A tuple of the original data and a list of identified dates.

addresses(data):-
Identifies addresses in the text data combining spaCy's location entities and CommonRegex's street addresses.

Parameters:
data: The text data to process.
Returns:
A tuple of the original data and a list of identified addresses.

phones(data):-
Detects phone numbers in the text data using CommonRegex.

Parameters:

data: The text data to process.
Returns:
A tuple of the original data and a list of identified phone numbers.

redact(data, names_list, dates_list, address_list, phones_list):-
Performs redaction of specified data categories within the text data and collects statistics.

Parameters:

data: The text data to process.
names_list: List of names to redact.
dates_list: List of dates to redact.
address_list: List of addresses to redact.
phones_list: List of phone numbers to redact.
Returns:

Redacted text data and a dictionary containing statistics of the redaction process.
save_censored_file(original_path, data, output_folder, suffix)
Saves the redacted text data to a new file with a specified suffix in the output directory.

Parameters:

original_path: The path of the original text file.
data: The redacted text data to save.
output_folder: The directory to save the redacted file.
suffix: The suffix to append to the filename.
process_files(input_pattern, output_folder, redact_names_flag, redact_dates_flag, redact_phones_flag, redact_addresses_flag, stats_output)
Processes multiple files based on a glob pattern, applying redaction as specified and generating statistics.

Parameters:

input_pattern: Glob pattern for files to process.
output_folder: Directory for saving redacted files.
redact_names_flag: Flag to redact names.
redact_dates_flag: Flag to redact dates.
redact_phones_flag: Flag to redact phone numbers.
redact_addresses_flag: Flag to redact addresses.
stats_output: Specifies where to output statistics (stdout, stderr, or filename).

Statistics Output Format
The statistics provide a summary for each processed file, including:

File name.
Count and positions of each censored item by category (names, dates, addresses, phone numbers).
Example:
File: example.txt
Names: Count = 2, Positions = [()]

