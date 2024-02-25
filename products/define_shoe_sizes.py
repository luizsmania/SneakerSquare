from products.models import Product


# Define a function to update has_shoe_sizes for products with specific criteria
def update_has_shoe_sizes():
    # Retrieve products with specific criteria (e.g., IDs 1, 2, and 3)
    products_to_update = Product.objects.filter(id__in=[1, 2, 3])

    # Update has_shoe_sizes field for each product
    for product in products_to_update:
        # Define your logic here to determine if the product has shoe sizes
        # For example, you can check if the product belongs to a specific category or has certain attributes
        # For demonstration purposes, let's assume all products with IDs 1, 2, and 3 have shoe sizes
        product.has_shoe_sizes = True

        # Save the updated product
        product.save()

        # Print the details of the updated product
        print(f"Product ID: {product.id}, Name: {product.name}, has_shoe_sizes: {product.has_shoe_sizes}")

# Call the function to update has_shoe_sizes
update_has_shoe_sizes()
