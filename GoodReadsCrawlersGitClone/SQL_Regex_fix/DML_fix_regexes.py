import re
import os
import pyperclip
import json


# (?:(?<=,)|^)(https?://(?:www\.)?goodreads\.com/[^,\n\r]+)(?:,(?=.*(https?://(?:www\.)?goodreads\.com/[^,\n\r]+)))

#! s'(?!,\s(?:\);|'))           s\\'

#! \s'(\w+)'\s               \s\'$1\'\s

#! (\w)'(\w)                 $1\'$2

#!   (\w)'(?!(?:\);|,))     $1\'

#!   (?<!,) '(\w)              \'$1

#!   (?<=[A-Za-z])'(?=, [A-Za-z])     \'
#,\s+'.*'.*?'(?:\);|,)

# pattern = r"'[^']*'(*SKIP)(*FAIL)|'"

# pattern = r"(?<=')(.*?)(?='[^']*$)"
# def getFieldValues(sql_insert):
#     sql_insert = sql_insert[sql_insert.index(') VALUES (')+10: ]
#     # Parse values from the SQL INSERT statement
#     # pat = r"(?:'((?:[^']|'')*)'|NULL|[\d.]+)(?:\s*,|$)"
#     values = re.findall(, sql_insert)

#     # Clean up the extracted values
#     cleaned_values = [value.replace("''", "'") if value.startswith("'") else value for value in values]

#     print(cleaned_values)
def escape_quotes(match):
    """
    Function to escape single quotes within string literals
    """
    return match.group(0).replace("'", "\\'")

def backtrack_get_field_values(n):
    # n is number of comma seperated values expected
    comma_counter = 0
    values = []
    

    
with open('author.txt','r',encoding='utf-8') as file:
    lines = file.readlines()
    sql_insert = lines[4]
    # print(line,end="\n\n\r")
    # fixed_line = re.sub(pattern, escape_quotes,line )
    # pyperclip.copy(fixed_line)
    # print(fixed_line)
    #TODO sql_insert = sql_insert[sql_insert.index(') VALUES (')+10: ]
    # Regular expression pattern to match keys inside parentheses
    keys_pattern = r"author \((.*?)\)"

    # Regular expression pattern to match values inside parentheses
    values_pattern = r"VALUES \((.*?)\)"

    # Regular expression pattern to match individual keys
    key_pattern = r"(\w+)(?:,|\))"

    # Regular expression pattern to match individual values (either numbers, strings, or NULL)
    value_pattern = r"'([^']*)'|NULL|([\d.]+)"


    # Parse keys from the SQL INSERT statement
    keys_match = re.search(keys_pattern, sql_insert)
    if keys_match:
        keys_str = keys_match.group(1)
        keys = re.findall(key_pattern, keys_str)
    else:
        keys = []

    # Parse values from the SQL INSERT statement
    values_match = re.search(values_pattern, sql_insert)
    

    if values_match:
        values_str = values_match.group(1)
        values = []
        for match in re.finditer(value_pattern, values_str):
            value = match.group(1)
            if value is None:
                value = match.group(2)
            values.append(value.strip())
    else:
        values = []

    # Construct the dictionary
    result_dict = dict(zip(keys, values))

    print(json.dumps(result_dict,indent=4))







