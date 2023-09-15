import os
from dotenv import load_dotenv
import csv
import requests

# Load environment variables from .env file
load_dotenv()


def get_recipe(ingredient):
    user_id = os.getenv("USER_ID")
    api_key = os.getenv("API_KEY")
    url = f'https://api.edamam.com/search?q={ingredient}&app_id={user_id}&app_key={api_key}'
    response = requests.get(url)
    recipe_data = response.json()

    return recipe_data.get('hits', [])


def run():
    ingredient = input("Please enter the recipe ingredient: ")
    filter_option = input("Do you want to filter by a health label? (yes/no): ").strip().lower()

    if filter_option == "yes":
        user_label = input("Please enter the health label you want to filter by: ").strip().lower()
        results = get_recipe(ingredient)
        found_recipes = []

        for result in results:
            recipe = result['recipe']
            health_labels = [label.lower().strip() for label in recipe.get('healthLabels', [])]

            if user_label in health_labels:
                found_recipes.append(recipe)

        if found_recipes:
            print("Recipes found with the specified label:")
            for recipe in found_recipes:
                print("Name:", recipe.get('label', 'N/A'))
                print("Calories:", recipe.get('calories', 'N/A'))
                print("Diet Labels:", ', '.join(recipe.get('dietLabels', [])))
                print("Health Labels:", ', '.join(recipe.get('healthLabels', [])))
                print("Ingredients:", ', '.join(recipe.get('ingredientLines', [])))

            save_to_csv(found_recipes)  # Call save_to_csv here
        else:
            print("No recipes found with the specified label.")
    elif filter_option == "no":
        results = get_recipe(ingredient)
        all_recipes = []

        if results:
            print("All recipes:")
            for result in results:
                recipe = result['recipe']
                all_recipes.append(recipe)
                print("Name:", recipe.get('label', 'N/A'))
                print("Calories:", recipe.get('calories', 'N/A'))
                print("Diet Labels:", ', '.join(recipe.get('dietLabels', [])))
                print("Health Labels:", ', '.join(recipe.get('healthLabels', [])))
                print("Ingredients:", ', '.join(recipe.get('ingredientLines', [])))
            # save_to_csv here
            save_to_csv(all_recipes)
        else:
            print("No recipes found.")
    else:
        print("Invalid option. Please enter 'yes' or 'no'.")


def save_to_csv(recipe_list):
    filename = 'output2Recipe.csv'
    with open(filename, 'w', newline='') as csv_recipe_file:
        header_row = "{:<40}{:<10}{:<40}{:<40}{:<80}\n".format(
            "Name", "Calories", "Diet Labels", "Health Labels", "Ingredients"
        )
        csv_recipe_file.write(header_row)

        for recipe in recipe_list:
            name = recipe.get('label', 'N/A')
            calories = recipe.get('calories', 'N/A')
            diet_labels = ', '.join(recipe.get('dietLabels', []))
            health_labels = ', '.join(recipe.get('healthLabels', []))
            ingredients = ', '.join(recipe.get('ingredientLines', []))

            row = "{:<40}{:<10}{:<40}{:<40}{:<80}\n".format(
                name, calories, diet_labels, health_labels, ingredients
            )
            csv_recipe_file.write(row)


if __name__ == "__main__":
    run()
