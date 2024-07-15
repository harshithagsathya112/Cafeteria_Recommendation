import unittest
from unittest.mock import patch
from io import StringIO

def handle_input_request(prompt):
    response = input(prompt)
    return response

def validate_input(prompt, valid_options=None):
    while True:
        response = input(prompt).strip()
        if response in valid_options or valid_options is None:
            return response
        else:
            print(f"Invalid input. Please enter one of the following: {', '.join(valid_options)}")

def update_profile_input():
    dietary_preference = validate_input(
        "1) Please select one - Vegetarian, Non Vegetarian, Eggetarian: ", 
        ['Vegetarian', 'Non Vegetarian', 'Eggetarian']
    )
    spice_level = validate_input(
        "2) Please select your spice level - High, Medium, Low: ", 
        ['High', 'Medium', 'Low']
    )
    preferred_cuisine = validate_input(
        "3) What do you prefer most? - North Indian, South Indian, Other: ", 
        ['North Indian', 'South Indian', 'Other']
    )
    sweet_tooth = validate_input(
        "4) Do you have a sweet tooth? - Yes, No: ", 
        ['Yes', 'No']
    )
    
    sweet_tooth = 1 if sweet_tooth == 'Yes' else 0

    return [dietary_preference, spice_level, preferred_cuisine, sweet_tooth]

class TestInputFunctions(unittest.TestCase):
    @patch('builtins.input', side_effect=['Vegetarian'])
    def test_handle_input_request(self, mock_input):
        response = handle_input_request("Please enter your dietary preference: ")
        self.assertEqual(response, 'Vegetarian')

    @patch('builtins.input', side_effect=['Invalid', 'Vegetarian'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_input_with_retry(self, mock_stdout, mock_input):
        response = validate_input("Please select one - Vegetarian, Non Vegetarian, Eggetarian: ", 
                                  ['Vegetarian', 'Non Vegetarian', 'Eggetarian'])
        self.assertEqual(response, 'Vegetarian')
        self.assertIn("Invalid input. Please enter one of the following: Vegetarian, Non Vegetarian, Eggetarian", mock_stdout.getvalue())

    @patch('builtins.input', side_effect=['Vegetarian', 'Medium', 'South Indian', 'Yes'])
    def test_update_profile_input(self, mock_input):
        profile = update_profile_input()
        expected_profile = ['Vegetarian', 'Medium', 'South Indian', 1]
        self.assertEqual(profile, expected_profile)

if __name__ == "__main__":
    unittest.main()
