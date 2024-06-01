from .models import Wishlist  # Import the Wishlist model

def counter(request):
    wishlist_count = 0  # Initialize the wishlist count

    if 'admin' in request.path:
        return {}
    else:
        if request.user.is_authenticated:  # Check if the user is authenticated
            try:
                # Retrieve the wishlist items for the current user
                wishlist_items = Wishlist.objects.filter(user=request.user)
                # Calculate the total count of wishlist items
                wishlist_count = wishlist_items.count()
            except Wishlist.DoesNotExist:
                wishlist_count = 0  # If no wishlist items found, set count to 0

    # Return a dictionary containing the wishlist count
    return {'wishlist_count': wishlist_count}
