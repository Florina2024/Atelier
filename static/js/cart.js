var updateBtns = document.getElementsByClassName('update-cart');

for ( var i=0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        var size = this.dataset.size;
        var color = this.dataset.color;
        console.log('productId:', productId, 'action:', action, 'size', size, 'color', color);

        console.log('USER:',user);
        if (user=== 'AnonymousUser'){
            addCookieItem(productId, action, size, color);
        }else{
            updateUserOrder(productId, action, size, color)
        }
    })
}

document.addEventListener("DOMContentLoaded", function () {
    let removeButtons = document.querySelectorAll(".remove-item");

    removeButtons.forEach(button => {
        button.addEventListener("click", function () {
            let productId = this.dataset.product;
            let size = this.dataset.size;
            let action = this.dataset.action;  // Always 'remove'

            console.log("Removing item:", productId, "Size:", size);
            updateUserOrder(productId, action, size);
        });
    });
});

function addCookieItem(productId, action, size, color) {
    console.log('Not logged in...');

    // Check the action type (add or remove)
    if(action == 'add') {
        // If product is not in the cart, add it with quantity 1
        if(cart[productId] == undefined) {
            cart[productId] = { 'quantity': 1, 'size': size, 'color': color  };
            console.log('Added to cart:', cart[productId]);
        } else {
            // If the product is already in the cart, increase the quantity
            cart[productId]['quantity'] += 1;
            cart[productId]['size'] = size; // update size if needed
            console.log('Updated cart:', cart[productId]);
        }

        // Show the add message
        const messageBox = document.getElementById('add-message');
        if (messageBox) {
            messageBox.classList.remove('hidden');
        }


    } else if(action == 'remove') {
        // Check if the product exists in the cart
        if(cart[productId]) {
            // Decrease the quantity of the product
            cart[productId]['quantity'] -= 1;

            // If quantity is 0 or less, remove the product from the cart
            if(cart[productId]['quantity'] <= 0) {
                console.log('Removing item:', productId);
                delete cart[productId];
            }
        }
    }

    // Log the current cart to check its state
    console.log('Cart:', cart);

    // Save the updated cart in the cookie
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";

    // Reload the page to update the cart view
    setTimeout(function() {
        window.location.reload(true);
    }, 1500);
}
//function updateUserOrder(productId, action, size) {
//    console.log('User is logged in, sending data.');
//
//    let url = '/update_item/';
//    fetch(url, {
//        method: 'POST',
//        headers: {
//            'Content-Type': 'application/json',
//            'X-CSRFToken': csrftoken
//        },
//        body: JSON.stringify({
//            'productId': productId,
//            'action': action,
//            'size': size
//        })
//    })
//    .then(response => response.json())
//    .then(data => {
//        console.log('Success:', data);
//        location.reload();
//    })
//    .catch(error => console.error('Error:', error));
//}
function updateUserOrder(productId, action, size, color){
    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action, 'size': size})
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('Data:', data)
        // Rifresko faqen që të shfaqet quantity dhe çmimi i ri
        location.reload()
    })
}



