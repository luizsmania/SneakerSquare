from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.safestring import mark_safe


from .models import Product, Category, Comment, WishlistItem
from .forms import ProductForm, CommentForm
from .models import WishlistItem

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None
    current_page_url = request.get_full_path()
    request.session['previous_page'] = current_page_url
    shoe_sizes = ['2.5', '3', '3.5', '4', '4.5', '5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12', '13', '14']
    clothes_sizes = ['XS', 'S', 'M', 'L', 'XL']
    
    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)
            
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
        'clothes_sizes': clothes_sizes,
        'shoe_sizes': shoe_sizes,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)
    comments = Comment.objects.filter(product=product)
    request.session['previous_page'] = request.path  # Set the current page URL

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.product = product
            new_comment.save()
            messages.success(request, 'Your comment has been added successfully.')
            return redirect('product_detail', product_id=product_id)
    else:
        form = CommentForm()

    context = {
        'product': product,
        'comments': comments,
        'form': form,
    }
    return render(request, 'products/product_detail.html', context)
@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))

@login_required
def add_comment(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = product
            comment.save()
            messages.success(request, 'Your comment has been added successfully.')
            return redirect('product_detail', product_id=product_id)
        else:
            messages.error(request, 'Failed to add comment. Please check the form.')
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.user:
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'You are not authorized to delete this comment.')
    return redirect('product_detail', product_id=comment.product.id)

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    # Check if the product is already in the user's wishlist
    if WishlistItem.objects.filter(user=request.user, product=product).exists():
        # Product is already in wishlist, do nothing
        wishlist_url = '/products/wishlist/'  # Specify the URL of the wishlist page
        message = f'Product "{product.name}" is already in your <a href="{wishlist_url}">wishlist</a>.'
        messages.error(request, mark_safe(message))
    else:
        # Add product to wishlist
        WishlistItem.objects.create(user=request.user, product=product)
        wishlist_url = '/products/wishlist/'  # Specify the URL of the wishlist page
        message = f'Product "{product.name}" was added to your <a href="{wishlist_url}">wishlist</a>.'
        messages.success(request, mark_safe(message))
    
    # Get the previous page URL from the session or set a default URL
    previous_page = request.session.get('previous_page', 'products')  # Change 'products' to your default URL
    
    # Redirect back to the previous page
    return redirect(previous_page)

def wishlist_view(request):
    # Retrieve wishlist items for the current user
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'wishlist.html', context)

def delete_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id)
    product_name = item.product.name  # Get the product name before deleting
    
    # Specify the URL of the wishlist page
    wishlist_url = '/products/wishlist/'
    
    # Create the success message with the correct product name and wishlist URL
    message = f'Product "{product_name}" was deleted from your <a href="{wishlist_url}">wishlist</a>.'
    
    # Add the success message
    messages.success(request, mark_safe(message))
    
    # Delete the item from the wishlist
    item.delete()

    return redirect('wishlist')  # Assuming 'wishlist' is the name of your wishlist view