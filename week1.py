import os
import random
class ProductCatalog:
    """
    A class to represent a product catalog with search functionality and random product generation.
    Attributes:
        product (str): The name of the product to be queried.
        products (list): A list of dictionaries representing the product database.
    Methods:
        __init__():
            Initializes the ProductCatalog instance with a default product name and a randomly generated product database.
        search(query: str) -> tuple:
            Searches for a product in the catalog by its name.
            Args:
                query (str): The name of the product to search for.
            Returns:
                tuple: A tuple containing a boolean indicating if the product was found, 
                       the number of iterations performed during the search, 
                       and the product details as a dictionary (empty if not found).
        generate_random_db() -> list:
            Generates a random product database with 100 entries, inserting the query product at a random position.
            Returns:
                list: A list of dictionaries representing the product database.
        generate_random_product(i: int) -> dict:
            Generates a random product with dummy data.
            Args:
                i (int): The unique identifier for the product.
            Returns:
                dict: A dictionary containing the details of the randomly generated product.
    """
    def __init__(self):
       self.product = "harness"
       self.products = self.generate_random_db()
       ##create a function to print the random
    
    def search(self,query:str):
        iterations = 0 
        for item in self.products:
            iterations +=1
            if query == item["name"]:
                return (True, iterations,item)
        else:
            return (False,iterations,{})

        
    def generate_random_db(self):
        query_product = {"id": 201, "name": f"{self.product}", "category": "harnesses", "brand": "Black Diamond", "price": 59.99, "stock": 20, "rating": 4.9}
        random_entry_point = random.randint(0,100)
        product_list = []
        for i in range(0,100):
            if i == random_entry_point:
                product_list.append(query_product)
            else:
            #generate random product
              product_list.append(self.generate_random_product(i))
        return product_list
    
    
    def generate_random_product(self,i):
        return {
                    "id": i,
                    "name": f"Product{i}",
                    "category": "random",
                    "brand": "random",
                    "price": 10.99,
                    "stock": 10,
                    "rating": 4.5
                }

    
def about():
    """
    Prints Program Flow
    """
    print("Linear Search Generator")
    print("this program generates a synthetic product catalog ")
    print("option 1 : create a catalog wiht sytnthetic data")
    print("option 2 : user can search for a product in the catalog. The only product that has a fixed name is harness")
    print("option 3 : batch test the search function.")
    print("this will create a dummy catalog and search for harness for the amount of cycles specified")
    print("It returns the Min, Max, and average steps it took to find the product")
    print("option 4 : About")
    print("option 4 : exit the program")

def print_item(item):
    """
    Prints the details of a search result.

    Args:
        item (tuple): A tuple containing three elements:
            - A boolean indicating whether the item was found (True/False).
            - An integer representing the number of iterations performed.
            - A dictionary containing details of the found item (if found).

    Behavior:
        - If the first element of the tuple is True, it prints the name of the 
          found item, the number of iterations, and all key-value pairs in the 
          details dictionary.
        - If the first element is False, it prints a message indicating that 
          the product was not found and the number of iterations performed.
    """
    if item[0] == True:
        print(f"Found {item[2]['name']} in {item[1]} iterations")
        print("****Details*******")
        for key,value in item[2].items():
            print(f"{key} : {value}")
    else:
        print(f"Product not found. in {item[1]} iterations")

def main_menu():
    while True:
        os.system("clear")
        print("Main Menu:")
        print("1. Create Catalog")
        print("2. Search Product")
        print("3. Batch Test")
        print("4. About")
        print("5. Exit")
        
        try:
            choice = int(input("Select an option: ").strip())
            if choice in {1, 2, 3, 4,  5}:
                return choice
            else:
                print("Invalid selection. Please choose a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            input("Press enter to continue")

def auto_test(cycles:int):
        """
        Simulates a series of automated tests on a product catalog and returns statistical results.

        Args:
            cycles (int): The number of test cycles to perform.

        Returns:
            tuple: A tuple containing the minimum, maximum, and average values of the second element 
                   from the search results across all test cycles.
        """
        steps = []
        for i in range(0,cycles):
            catalog = ProductCatalog()
            query = catalog.product
            item = catalog.search(query)
            #print(item[1])
            steps.append(item[1])
            #print(steps)
        return (min(steps),max(steps), sum(steps)/len(steps))

def control_loop():
    catalog = None 
    while True:
        menu_selection = main_menu()

        if menu_selection == 1:
            try:
                catalog = ProductCatalog()
            except Exception as e:
                print(f"Failed to create catalog: {e}")
            input("Press enter to continue")

        elif menu_selection == 2:
            if catalog is None:
                print("Catalog not created. Please create a catalog first.")
            else:
                try:
                    query = input("Enter product name: ")
                    item = catalog.search(query)
                    print_item(item)
                except Exception as e:
                    print(f"Error searching for product: {e}")
            input("Press enter to continue")
         
        elif menu_selection == 3:
            try:
               cycles = int(input("Enter number of cycles to test:"))
               results = auto_test(cycles)
               print(f"Out of {cycles} cycles, found item in Min: {results[0]} Max: {results[1]}, Avg: {results[2]}")
               input("Press enter to continue")
            except ValueError:
                print("Invalid input. Please enter a number.")
                input("Press enter to continue")
             

        elif menu_selection == 4:
            about()
            input("Press enter to continue")

        elif menu_selection == 5:
            print("Goodbye")
            break  

    
if __name__ == "__main__":
    control_loop()
  

