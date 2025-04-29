#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_logs.py
This script processes a CSV file containing user IDs, retrieves user information from Canvas using the Canvas API.
It then writes the results to a new CSV file with the same name prefixed by 'processed_'.

It adds new columns for user names and emails, and handles errors gracefully.
You need to have the 'canvasapi' library installed and a .env file with your Canvas API credentials.
Usage:
    # Install the required libraries, ideally in a venv if not already installed
    pip install canvasapi python-dotenv
    # Then run this command on the csv file generated from heroku
    # It should have the column headers of at least user_id that matches the Canvas API
    python parse_logs.py <csv_file>
Sample .env file:
    CANVAS_API_URL=https://your_canvas_instance.instructure.com
    CANVAS_API_KEY=your_api_key
"""

import csv
import sys
import os
import canvasapi
from dotenv import load_dotenv

def process_csv(file_name, canvas):
    try:
        with open(file_name, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            fieldnames = csv_reader.fieldnames + ['name'] + ['email'] # Add a new column for name and email
            output_file_name = f"processed_{os.path.basename(file_name)}"
            
            with open(output_file_name, mode='w', encoding='utf-8', newline='') as output_file:
                csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                csv_writer.writeheader()
                
                user_dict = {}
                for row in csv_reader:
                    user_id = row.get('user_id', 'N/A')
                    email = 'N/A'
                    name = ''
                    
                    # Using canvasapi, look up the user_id in Canvas. Use a local dict to cache results to avoid repeats
                    if user_id not in user_dict:
                        try:
                            user = canvas.get_user(user_id)
                            user_dict[user_id] = user
                            name = user.name
                            email = user.email
                            print(f"User found and stored: {user.name}")
                        except canvasapi.exceptions.ResourceDoesNotExist:
                            print(f"User with ID {user_id} does not exist.")
                    else:
                        name = user_dict[user_id].name
                        email = user_dict[user_id].email
                        print(f"User {user_id} already processed.")
                    
                    # Add the email to the row and write it to the new CSV
                    row['name'] = name
                    row['email'] = email
                    csv_writer.writerow(row)
        
        print(f"Processed file saved as '{output_file_name}'")
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_logs.py <csv_file>")
        sys.exit(1)

    csv_file_name = sys.argv[1]
    # Assuming you have a Canvas API client set up
    load_dotenv()
    canvas = canvasapi.Canvas(os.environ['CANVAS_API_URL'], os.environ['CANVAS_API_KEY'])
    process_csv(csv_file_name, canvas)
