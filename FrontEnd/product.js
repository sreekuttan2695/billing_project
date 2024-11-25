// Fetch all products on page load
document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
    // fetchCategories();  // Commenting out since it's not defined

    // Bind click event directly to the Add Product button
    const addButton = document.getElementById("addProductButton");
    addButton.addEventListener("click", (event) => {
        event.preventDefault();
        console.log("Add Product button clicked");
        addProduct();
    });
});



// Fetch Products Function
async function fetchProducts(searchQuery = '', selectedCategories = []) {
    const url = new URL('http://127.0.0.1:8000/api/product/');
    if (searchQuery) url.searchParams.append('search', searchQuery);
    selectedCategories.forEach(category => url.searchParams.append('categories', category));

    const response = await fetch(url, { method: 'GET', credentials: 'include' });
    const data = await response.json();

    if (response.ok) {
        renderProducts(data.products);
        renderCategories(data.categories); // Display unique categories
    } else {
        console.error("Error fetching products:", data);
    }
}

// Render Products in Table
function renderProducts(products) {
    const tableBody = document.getElementById("productTable").querySelector("tbody");
    tableBody.innerHTML = ""; // Clear existing rows

    products.forEach(product => {
        const row = document.createElement("tr");

        // Create cells with editable inputs for each field
        Object.entries(product).forEach(([key, value]) => {
            if (key !== "product_id" && key !== "client_id") { // Exclude primary key and client ID
                const cell = document.createElement("td");
                const input = document.createElement("input");
                input.type = "text";
                input.value = value;
                input.disabled = true; // Initially disabled for editing
                cell.appendChild(input);
                row.appendChild(cell);
            }
        });

        // Add action buttons (Edit and Delete)
        const actionCell = document.createElement("td");
        const editButton = document.createElement("button");
        editButton.innerText = "Edit";
        editButton.onclick = () => enableEdit(row, product.product_id);
        
        const deleteButton = document.createElement("button");
        deleteButton.innerText = "Delete";
        deleteButton.onclick = () => deleteProduct(product.product_id);

        actionCell.appendChild(editButton);
        actionCell.appendChild(deleteButton);
        row.appendChild(actionCell);

        tableBody.appendChild(row);
    });
}

// Render Category Filters
function renderCategories(categories) {
    const categoryFilters = document.getElementById("categoryFilters");
    categoryFilters.innerHTML = ""; // Clear existing filters

    categories.forEach(category => {
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = category;
        checkbox.onchange = () => applyFilters(); // Apply filter on change

        const label = document.createElement("label");
        label.innerText = category;

        categoryFilters.appendChild(checkbox);
        categoryFilters.appendChild(label);
    });
}

// Enable Row Editing
function enableEdit(row, productId) {
    row.querySelectorAll("input").forEach(input => input.disabled = false);
    const saveButton = document.createElement("button");
    saveButton.innerText = "Save";
    saveButton.onclick = () => saveProduct(row, productId);
    row.querySelector("td:last-child").appendChild(saveButton); // Append save button
}

// Save Edited Product
async function saveProduct(row, productId) {
    const data = {};
    const cells = row.querySelectorAll("td");

    // Collect data from inputs
    ["name", "HSN_code", "tax_percentage", "discount_rate", "unit", "category", "brand", "price_after_tax", "price_before_tax", "sales_rank"]
        .forEach((field, index) => data[field] = cells[index].querySelector("input").value);

    // Ensure numeric values for calculations
    const taxPercentage = parseFloat(data.tax_percentage) || 0; // Default to 0 if empty or invalid
    const priceBeforeTax = parseFloat(data.price_before_tax) || 0;
    const priceAfterTax = parseFloat(data.price_after_tax) || 0;

    // Auto-calculate missing price column based on user input
    if (priceBeforeTax && !priceAfterTax) {
        data.price_after_tax = (priceBeforeTax * (1 + taxPercentage / 100)).toFixed(2);
    } else if (!priceBeforeTax && priceAfterTax) {
        data.price_before_tax = (priceAfterTax / (1 + taxPercentage / 100)).toFixed(2);
    }

    data.product_id = productId;
    data.last_updated_by = "superadmin";  // Replace "superadmin" with the actual username if dynamic value is available

    const response = await fetch("http://127.0.0.1:8000/api/product/", {
        method: 'PUT',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include"
    });

    if (response.ok) {
        alert("Product updated successfully!");
        fetchProducts(); // Refresh product list
    } else {
        console.error("Failed to update product");
    }
}


// Delete Product
async function deleteProduct(productId) {
    const response = await fetch("http://127.0.0.1:8000/api/product/", {
        method: 'DELETE',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId }),
        credentials: "include"
    });

    if (response.ok) {
        alert("Product deleted successfully!");
        fetchProducts(); // Refresh product list
    } else {
        console.error("Failed to delete product");
    }
}
document.addEventListener("DOMContentLoaded", () => {
    const taxInput = document.getElementById("newProductTaxPercentage");
    const priceBeforeTaxInput = document.getElementById("newProductPriceBeforeTax");
    const priceAfterTaxInput = document.getElementById("newProductPriceAfterTax");

    function calculatePrice() {
        const taxPercentage = parseFloat(taxInput.value) || 0;

        // If Price Before Tax is filled, calculate Price After Tax
        if (document.activeElement === priceBeforeTaxInput && priceBeforeTaxInput.value) {
            const priceBeforeTax = parseFloat(priceBeforeTaxInput.value) || 0;
            const priceAfterTax = priceBeforeTax * (1 + taxPercentage / 100);
            priceAfterTaxInput.value = priceAfterTax.toFixed(2);
        }

        // If Price After Tax is filled, calculate Price Before Tax
        if (document.activeElement === priceAfterTaxInput && priceAfterTaxInput.value) {
            const priceAfterTax = parseFloat(priceAfterTaxInput.value) || 0;
            const priceBeforeTax = priceAfterTax / (1 + taxPercentage / 100);
            priceBeforeTaxInput.value = priceBeforeTax.toFixed(2);
        }
    }

    // Add event listeners for dynamic calculation
    taxInput.addEventListener("input", calculatePrice);
    priceBeforeTaxInput.addEventListener("input", calculatePrice);
    priceAfterTaxInput.addEventListener("input", calculatePrice);
});

// Add New Product
async function addProduct() {
    console.log("Adding product...");  // Debugging output
    const data = {
        name: document.getElementById("newProductName").value,
        HSN_code: document.getElementById("newProductHSNCode").value,
        tax_percentage: document.getElementById("newProductTaxPercentage").value,
		discount_rate: document.getElementById("newProductDiscountPercentage").value || 0, // Default to 0,
        unit: document.getElementById("newProductUnit").value,
        category: document.getElementById("newProductCategory").value,
        brand: document.getElementById("newProductBrand").value,
        price_after_tax: document.getElementById("newProductPriceAfterTax").value,
		price_before_tax: document.getElementById("newProductPriceBeforeTax").value,
        sales_rank: document.getElementById("newProductSalesRank").value,
        created_by: "superadmin",  // Or replace with dynamic user data if available
        last_updated_by: "superadmin"  // Or replace with dynamic user data if available
    };

    console.log("Sending POST request with data:", data);  // Debugging output
    const response = await fetch("http://127.0.0.1:8000/api/product/", {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include"
    });

    if (response.ok) {
        console.log("Product added successfully");  // Success debugging output
        alert("Product added successfully!");
        fetchProducts(); // Refresh product list
        // Clear the input fields
        document.querySelectorAll("#addProductTable input").forEach(input => input.value = '');
    } else {
        console.error("Failed to add product");
        const errorData = await response.json();
        console.error("Error response:", errorData);  // Output error response for debugging
    }
}


// Search Functionality
document.getElementById("searchButton").addEventListener("click", () => {
    const searchQuery = document.getElementById("searchBar").value;
    fetchProducts(searchQuery);
});

// Apply Category Filters
function applyFilters() {
    const selectedCategories = Array.from(document.querySelectorAll("#categoryFilters input:checked")).map(checkbox => checkbox.value);
    fetchProducts(document.getElementById("searchBar").value, selectedCategories);
}
