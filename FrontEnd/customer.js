document.addEventListener("DOMContentLoaded", () => {
    fetchCustomers();

    document.getElementById("addCustomerButton").addEventListener("click", (event) => {
        event.preventDefault();
        addCustomer();
    });

    document.getElementById("searchButton").addEventListener("click", () => {
        const searchQuery = document.getElementById("searchBar").value;
        fetchCustomers(searchQuery);
    });
});

async function fetchCustomers(searchQuery = '') {
    const url = new URL('http://127.0.0.1:8000/api/customer/');
    if (searchQuery) url.searchParams.append('search', searchQuery);

    const response = await fetch(url, { method: 'GET', credentials: 'include' });
    const data = await response.json();

    if (response.ok) {
        renderCustomers(data.customers);
    } else {
        console.error("Error fetching customers:", data);
    }
}

function renderCustomers(customers) {
    const tableBody = document.getElementById("customerTable").querySelector("tbody");
    tableBody.innerHTML = "";

    customers.forEach(customer => {
        const row = document.createElement("tr");

        Object.entries(customer).forEach(([key, value]) => {
            if (key !== "customer_id" && key !== "client_id" && key !== "created_on" && key !== "created_by" && key !== "last_updated_on" && key !== "last_updated_by") {
                const cell = document.createElement("td");
                const input = document.createElement("input");
                input.type = "text";
                input.value = value;
                input.disabled = true;
                cell.appendChild(input);
                row.appendChild(cell);
            }
        });

        const actionCell = document.createElement("td");
        const editButton = document.createElement("button");
        editButton.innerText = "Edit";
        editButton.onclick = () => enableEdit(row, customer.customer_id);

        const deleteButton = document.createElement("button");
        deleteButton.innerText = "Delete";
        deleteButton.onclick = () => deleteCustomer(customer.customer_id);

        actionCell.appendChild(editButton);
        actionCell.appendChild(deleteButton);
        row.appendChild(actionCell);

        tableBody.appendChild(row);
    });
}

function enableEdit(row, customerId) {
    row.querySelectorAll("input").forEach(input => input.disabled = false);
    const saveButton = document.createElement("button");
    saveButton.innerText = "Save";
    saveButton.onclick = () => saveCustomer(row, customerId);
    row.querySelector("td:last-child").appendChild(saveButton);
}

async function addCustomer() {
    const data = {
        name: document.getElementById("newCustomerName").value,
        address: document.getElementById("newCustomerAddress").value,
        phone: document.getElementById("newCustomerPhone").value,
        email_id: document.getElementById("newCustomerEmail").value,
        category: document.getElementById("newCustomerCategory").value,
        GSTIN: document.getElementById("newCustomerGSTIN").value,
        sales_rank: document.getElementById("newCustomerSalesRank").value
    };

    const response = await fetch("http://127.0.0.1:8000/api/customer/", {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include"
    });

    if (response.ok) {
        alert("Customer added successfully!");
        fetchCustomers();
    } else {
        console.error("Failed to add customer");
    }
}

async function saveCustomer(row, customerId) {
    const data = {};
    const cells = row.querySelectorAll("td");

    ["name", "address", "phone", "email_id", "category", "GSTIN", "sales_rank"]
        .forEach((field, index) => data[field] = cells[index].querySelector("input").value);

    data.customer_id = customerId;

    const response = await fetch("http://127.0.0.1:8000/api/customer/", {
        method: 'PUT',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include"
    });

    if (response.ok) {
        alert("Customer updated successfully!");
        fetchCustomers();
    } else {
        console.error("Failed to update customer");
    }
}

async function deleteCustomer(customerId) {
    const response = await fetch("http://127.0.0.1:8000/api/customer/", {
        method: 'DELETE',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_id: customerId }),
        credentials: "include"
    });

    if (response.ok) {
        alert("Customer deleted successfully!");
        fetchCustomers();
    } else {
        console.error("Failed to delete customer");
    }
}
