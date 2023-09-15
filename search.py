import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
from dotenv import load_dotenv
import csv

root = tk.Tk()
root.title("Search")
root.configure(bg="pink")

# Load environment variables from .env file
load_dotenv()

# Create a custom ttk style for the Treeview
style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 14), padding=5)


# Function to fetch recipes based on the entered keyword
def fetch_recipes(title, user_id, api_key):
    # Construct the URL without health labels
    url = 'https://api.edamam.com/search?q={}&app_id={}&app_key={}'.format(title, user_id, api_key)

    response = requests.get(url)

    # Check the response status code
    if response.status_code == 200:
        try:
            response_json = response.json()
            recipes = response_json.get('hits', [])
            return recipes
        except ValueError:
            return []
    else:
        # Handle the case where the API request was not successful
        return []


# Function to get recipes based on selected diet labels
def get_recipe():
    title = entry_task.get("1.0", tk.END).strip()
    user_id = os.getenv("USER_ID")
    api_key = os.getenv("API_KEY")

    recipes = fetch_recipes(title, user_id, api_key)

    # Get the selected diet labels from the check buttons
    selected_labels = [label_text for label_text, var in zip(diet_labels_list, label_vars) if var.get() == "1"]

    # Filter recipes based on selected diet labels
    if selected_labels:
        filtered_recipes = [recipe for recipe in recipes if
                            all(label in recipe['recipe']['dietLabels'] for label in selected_labels)]
    else:
        filtered_recipes = recipes

    # Display the filtered results
    display_results(filtered_recipes)
    save_to_csv(filtered_recipes)

    # Clear the input field
    entry_task.delete("1.0", tk.END)


# Function to display the results in the Treeview
def display_results(recipe_list, tree=None):
    # Clear previous results
    for widget in result_frame.winfo_children():
        widget.destroy()

    if not recipe_list:
        result_label = tk.Label(result_frame, text="No matching recipes found", font=("Arial", 16), bg="pink")
        result_label.pack()
        return

    tree = ttk.Treeview(result_frame, columns=[
        "Name", "Calories", "Diet Labels", "Health Labels", "Ingredients"])

    # Set column widths and minimum widths for specific columns
    tree.column("#0", width=0, stretch="no")
    # Column for "Name"
    tree.column("Name", width=250, minwidth=250)
    # Column for "Calories"
    tree.column("Calories", width=100, minwidth=100)
    # Column for "Diet Labels"
    tree.column("Diet Labels", width=250, minwidth=250)
    # Column for "Health Labels"
    tree.column("Health Labels", width=250, minwidth=250)
    # Column for "Ingredients"
    tree.column("Ingredients", width=250, minwidth=250)

    # Set column headers
    tree.heading("Name", text="Name")
    tree.heading("Calories", text="Calories")
    tree.heading("Diet Labels", text="Diet Labels")
    tree.heading("Health Labels", text="Health Labels")
    tree.heading("Ingredients", text="Ingredients")

    hsb = ttk.Scrollbar(tree, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)
    tree.pack(expand=True, fill="both")
    hsb.pack(side="bottom", fill="x")

    for recipe in recipe_list:
        if 'recipe' in recipe:
            recipe = recipe['recipe']
            name = recipe.get('label', 'N/A')
            calories = str(recipe.get('calories', 'N/A'))
            diet_labels = ', '.join(recipe.get('dietLabels', []))
            health_labels = ', '.join(recipe.get('healthLabels', []))
            ingredients = ', '.join(recipe.get('ingredientLines', []))

            tree.insert("", "end", values=(name, calories, diet_labels, health_labels, ingredients))


# Function to save the results to a CSV file
def save_to_csv(recipe_list):
    filename = 'outputRecipe.csv'
    with open(filename, 'w', newline='') as csv_recipe_file:
        header_row = "{:<40}{:<20}{:<40}{:<40}{:<80}{:<20}\n".format(
            "Name", "Calories", "Diet Labels", "Health Labels", "Ingredients", "Health Label"
        )
        csv_recipe_file.write(header_row)

        for result in recipe_list:
            recipe = result['recipe']
            name = recipe.get('label', 'N/A').replace('|', ' ')
            calories = str(recipe.get('calories', 'N/A')).replace('|', ' ')
            diet_labels = ', '.join(recipe.get('dietLabels', [])).replace('|', ' ')
            health_labels = ', '.join(recipe.get('healthLabels', [])).replace('|', ' ')
            ingredients = ', '.join(recipe.get('ingredientLines', [])).replace('|', ' ')
            health_label = ', '.join(recipe.get('healthLabels', [])).replace('|', ' ')

            row = "{:<40}{:<20}{:<40}{:<40}{:<80}{:<20}\n".format(
                name, calories, diet_labels, health_labels, ingredients, health_label
            )
            csv_recipe_file.write(row)


# UI
label = tk.Label(root, text="Enter recipe to search", font=("Arial", 14), bg="pink")
label.pack(pady=30)

entry_task = tk.Text(root, width=50, height=2)
entry_task.pack(pady=10)

button_search = tk.Button(root, text="Search", width=20, height=2, command=get_recipe)
button_search.pack(pady=10)

# Create check buttons for diet labels
# Define the diet labels list
diet_label_frame = tk.Frame(root, bg="pink")
diet_label_frame.pack(pady=10)
diet_labels_list = [
    "Low-Fat", "Low-Carb", "High-Fiber", "High-Protein", "Low-Sodium", "Low-Sugar"
]

# Create a list to hold the diet label variables
label_vars = []

for label_text in diet_labels_list:
    var = tk.StringVar(value="0")
    check_button = tk.Checkbutton(
        diet_label_frame, text=label_text, variable=var, bg="pink", onvalue="1", offvalue="0"
    )
    check_button.grid(row=len(label_vars) // 3, column=len(label_vars) % 3, padx=5, pady=5, sticky="w")
    label_vars.append(var)

# Create a frame for the result display
result_frame = tk.Frame(root, bg="pink")
result_frame.pack(expand=True, fill="both")

root.mainloop()
