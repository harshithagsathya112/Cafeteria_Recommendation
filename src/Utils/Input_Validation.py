DIETARY_OPTIONS = ['Vegetarian', 'Non Vegetarian', 'Eggetarian']
SPICE_LEVEL_OPTIONS = ['High', 'Medium', 'Low']
CUISINE_OPTIONS = ['North Indian', 'South Indian', 'Other']
SWEET_TOOTH_OPTIONS = ['Yes', 'No']

def handle_input_request(prompt):
    response = input(prompt)
    return response

def validate_input(prompt, valid_options=None):
    while True:
        response = input(prompt).strip()
        if valid_options is None or response in valid_options:
            return response
        else:
            print(f"Invalid input. Please enter one of the following: {', '.join(valid_options)}")

def update_profile_input():
    dietary_preference = validate_input(
        "1) Please select one - Vegetarian, Non Vegetarian, Eggetarian: ", 
        DIETARY_OPTIONS
    )
    spice_level = validate_input(
        "2) Please select your spice level - High, Medium, Low: ", 
        SPICE_LEVEL_OPTIONS
    )
    preferred_cuisine = validate_input(
        "3) What do you prefer most? - North Indian, South Indian, Other: ", 
        CUISINE_OPTIONS
    )
    sweet_tooth = validate_input(
        "4) Do you have a sweet tooth? - Yes, No: ", 
        SWEET_TOOTH_OPTIONS
    )

    sweet_tooth = True if sweet_tooth == 'Yes' else False

    return [dietary_preference, spice_level, preferred_cuisine, sweet_tooth]
