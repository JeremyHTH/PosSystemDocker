// validation.js
// console.log("Hello, world!");


function validatePurchaseForm(event) {
    // Prevent the form from submitting
    console.log("Ran");
    event.preventDefault();

    // Get form values
    const productId = document.getElementById('purchase_product_id').value;
    const purchasePrice = document.getElementById('purchase_price').value;
    const quantity = document.getElementById('purchase_quantity').value;
    const purchaseDate = document.getElementById('purchase_date').value;

    // Error messages
    if (productId < 0) {
        alert("Error: Product ID must be non-negative.");
        return false;
    }
    if (purchasePrice < 0) {
        alert("Error: Purchase price must be greater than zero.");
        return false;
    }
    if (quantity < 0) {
        alert("Error: Quantity must be greater than zero.");
        return false;
    }
    if (!purchaseDate) {
        alert("Error: Purchase date must be provided.");
        return false;
    }

    // If validation passes, submit the form
    document.getElementById('purchaseForm').submit();
}

function validateSalesForm(event) {
    // Prevent the form from submitting
    console.log("Ran sale button ");
    event.preventDefault();

    // Get form values
    const productId = document.getElementById('sale_product_id').value;
    const sellingPrice = document.getElementById('selling_price').value;
    const quantity = document.getElementById('sale_quantity').value;
    const salesDate = document.getElementById('sales_date').value;

    // Error messages
    if (productId < 0) {
        alert("Error: Product ID must be non-negative.");
        return false;
    }
    if (sellingPrice < 0) {
        alert("Error: Selling price must be greater than zero.");
        return false;
    }
    if (quantity < 0) {
        alert("Error: Quantity must be greater than zero.");
        return false;
    }
    if (!salesDate) {
        alert("Error: Sales date must be provided.");
        return false;
    }

    // If validation passes, submit the form
    document.getElementById('salesForm').submit();
}


function updateProcessed(type, id, status) {
    fetch(`/update_processed`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type, id, processed: status })
    })
    .then(response => {
        if (!response.ok) {
            alert('Failed to update processed status');
        }
    })
    .catch(error => console.error('Error:', error));
}
