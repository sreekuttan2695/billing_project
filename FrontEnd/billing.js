document.addEventListener("DOMContentLoaded", () => {
    const customerNameInput = document.getElementById("customerName");
    const suggestionBox = document.getElementById("suggestionBox");
    const modal = document.getElementById("addCustomerModal");
    const closeModalButton = document.getElementById("closeModal");
    const addNewCustomerButton = document.getElementById("addNewCustomerButton");
    const today = new Date().toISOString().split('T')[0];
    document.getElementById("invoiceDate").value = today; // Set default date to today

    // Show the modal when "Add New Customer" is clicked
    addNewCustomerButton.addEventListener("click", () => {
        modal.style.display = "block";
    });

    // Close the modal
    closeModalButton.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Handle typing in the name input for suggestions
    customerNameInput.addEventListener("input", async () => {
        const query = customerNameInput.value.trim();
        if (query.length < 1) {
            suggestionBox.innerHTML = "";
            return;
        }

        const response = await fetch(`http://127.0.0.1:8000/api/customer/?search=${query}`, {
            method: "GET",
            credentials: "include",
        });

        const data = await response.json();
        renderSuggestions(data.customers);
    });

    // Render suggestions
    function renderSuggestions(customers) {
        suggestionBox.innerHTML = ""; // Clear previous suggestions

        if (customers.length === 0) {
            const noResultRow = document.createElement("div");
            noResultRow.innerText = "No customers found.";
            suggestionBox.appendChild(noResultRow);

            return;
        }

        customers.slice(0, 5).forEach(customer => {
            const suggestion = document.createElement("div");
            suggestion.innerText = `Name: ${customer.name}, Phone: ${customer.phone}`;
            suggestion.onclick = () => autofillCustomerDetails(customer);
            suggestionBox.appendChild(suggestion);
        });
    }

    // Autofill customer details into the form
    function autofillCustomerDetails(customer) {
        document.getElementById("customerName").value = customer.name;
        document.getElementById("customerPhone").value = customer.phone;
        document.getElementById("customerAddress").value = customer.address || "";
        document.getElementById("customerGSTIN").value = customer.gstin || "";
        suggestionBox.innerHTML = ""; // Clear suggestions
    }

    // Handle the Add Customer form submission
    document.getElementById("addCustomerForm").addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            name: document.getElementById("addName").value,
            phone: document.getElementById("addPhone").value,
            address: document.getElementById("addAddress").value,
            gstin: document.getElementById("addGSTIN").value,
            category: document.getElementById("addCategory").value,
            sales_rank: document.getElementById("addSalesRank").value,
        };

        const response = await fetch("http://127.0.0.1:8000/api/customer/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
            credentials: "include",
        });

        if (response.ok) {
            alert("Customer added successfully!");

            const addedCustomer = await response.json(); // Get newly added customer details
            document.getElementById("customerName").value = addedCustomer.name;
            document.getElementById("customerPhone").value = addedCustomer.phone;
            document.getElementById("customerAddress").value = addedCustomer.address || "";
            document.getElementById("customerGSTIN").value = addedCustomer.gstin || "";

            modal.style.display = "none"; // Close modal
        } else {
            console.error("Failed to add customer.");
        }
    });
	document.getElementById("billingDetailsForm").addEventListener("submit", (e) => {
        e.preventDefault();
        
        const placeOfSupply = document.getElementById("placeOfSupply").value;
        const invoiceDate = document.getElementById("invoiceDate").value;
        const rcm = document.getElementById("rcmCheckbox").checked;

        console.log({
            placeOfSupply,
            invoiceDate,
            rcm
        });

        // Perform additional operations like including this data in a billing request
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const productTable = document.getElementById("productTable");

    // Handle input in the product name column
    productTable.addEventListener("input", async (event) => {
        if (event.target.classList.contains("product-name")) {
            const query = event.target.value.trim();
            if (query.length > 0) {
                const response = await fetch(`http://127.0.0.1:8000/api/product/?search=${query}`, {
                    method: "GET",
                    credentials: "include",
                });

                const data = await response.json();
                renderProductSuggestions(event.target, data.products);
            }
        }
    });

    // Render product suggestions
    function renderProductSuggestions(inputElement, products) {
        let suggestionBox = document.querySelector(".product-suggestions");
        if (!suggestionBox) {
            suggestionBox = document.createElement("div");
            suggestionBox.classList.add("product-suggestions");
            suggestionBox.style.position = "absolute";
            suggestionBox.style.backgroundColor = "#fff";
            suggestionBox.style.border = "1px solid #ccc";
            inputElement.parentNode.appendChild(suggestionBox);
        }
        suggestionBox.innerHTML = "";

        if (products.length === 0) {
            suggestionBox.innerHTML = "<div>No products found.</div>";
            return;
        }

        products.slice(0, 5).forEach(product => {
            const suggestion = document.createElement("div");
            suggestion.innerText = `${product.name} (${product.unit})`;
            suggestion.onclick = () => autofillProductDetails(inputElement, product);
            suggestionBox.appendChild(suggestion);
        });
    }

    // Autofill product details into the row
    function autofillProductDetails(inputElement, product) {
        const row = inputElement.closest("tr");
		row.querySelector(".product-name").value = product.name;
        row.querySelector(".unit").value = product.unit;
        row.querySelector(".price-before-tax").value = product.price_before_tax;
        row.querySelector(".discount").value = product.discount_rate;
        row.querySelector(".tax-rate").value = product.tax_percentage;
		const qtyInputFirstRow = row.querySelector(".qty");
		qtyInputFirstRow.addEventListener("input", () => {
			calculateRow(row); // Trigger calculation when qty changes
		});
        addNewRow(); // Add a new row for the next product
        clearSuggestions();
    }

    // Calculate Taxable Price and Total Amount
    function calculateRow(row) {
        const qty = parseFloat(row.querySelector(".qty").value) || 0;
        const priceBeforeTax = parseFloat(row.querySelector(".price-before-tax").value) || 0;
        const discount = parseFloat(row.querySelector(".discount").value) || 0;
        const taxRate = parseFloat(row.querySelector(".tax-rate").value) || 0;

        const taxablePrice = qty * (priceBeforeTax - discount);
        const totalAmount = taxablePrice + (taxablePrice * (taxRate / 100));

        row.querySelector(".taxable-price").value = taxablePrice.toFixed(2);
        row.querySelector(".total-amount").value = totalAmount.toFixed(2);
    }

    // Add a new row dynamically
    // Add a new row dynamically
	function addNewRow() {
		const productTable = document.getElementById("productTable");
		const newRow = productTable.querySelector("tbody").insertRow();

		newRow.innerHTML = `
			<td><input type="text" class="product-name" placeholder="Type product name" autocomplete="off"></td>
			<td><input type="number" class="qty" min="1"></td>
			<td><input type="text" class="unit" disabled></td>
			<td><input type="text" class="price-before-tax" disabled></td>
			<td><input type="text" class="discount" disabled></td>
			<td><input type="text" class="tax-rate" disabled></td>
			<td><input type="text" class="taxable-price" disabled></td>
			<td><input type="text" class="total-amount" disabled></td>
			<td><button type="button" class="delete-row">Delete</button></td>
		`;

		// Add event listener for qty input changes in the new row
		const qtyInput = newRow.querySelector(".qty");
		qtyInput.addEventListener("input", () => {
			calculateRow(newRow); // Trigger calculation when qty changes
		});

		// Add event listener for product name suggestions
		const productNameInput = newRow.querySelector(".product-name");
		productNameInput.addEventListener("input", async () => {
			const query = productNameInput.value.trim();
			if (query.length > 0) {
				const response = await fetch(`http://127.0.0.1:8000/api/product/?search=${query}`, {
					method: "GET",
					credentials: "include",
				});
				const data = await response.json();
				renderProductSuggestions(productNameInput, data.products);
			}
		});
	}


    // Handle row deletion
    productTable.addEventListener("click", (event) => {
        if (event.target.classList.contains("delete-row")) {
            const row = event.target.closest("tr");
            row.parentNode.removeChild(row);
        }
    });


    // Clear product suggestions
    function clearSuggestions() {
        const suggestionBox = document.querySelector(".product-suggestions");
        if (suggestionBox) {
            suggestionBox.remove();
        }
    }
});

// Billing calculations starts here
document.addEventListener("DOMContentLoaded", () => {
    const placeOfSupplyDropdown = document.getElementById("placeOfSupply");
    const otherDiscountInput = document.getElementById("otherDiscount");
    const summarySection = document.getElementById("summarySection");

    let clientPlaceOfSupply = "";

    // Fetch Client's Place of Supply
    async function fetchClientPlaceOfSupply() {
        const response = await fetch("http://127.0.0.1:8000/api/client/place_of_supply/", {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();
        if (response.ok) {
            clientPlaceOfSupply = data.place_of_supply;
        } else {
            console.error("Error fetching client place of supply:", data.message);
        }
    }

    // Calculate Taxes
    function calculateTaxes() {
        const productRows = document.querySelectorAll("#productTable tbody tr");
        const taxSummary = {}; // {taxRate: {taxableAmount: 0, sgst: 0, cgst: 0, igst: 0}}

        let totalBeforeTax = 0;
        let totalDiscount = 0;

        // Calculate taxable amounts and discounts
        productRows.forEach(row => {
            const qty = parseFloat(row.querySelector(".qty").value) || 0;
            const priceBeforeTax = parseFloat(row.querySelector(".price-before-tax").value) || 0;
            const discount = parseFloat(row.querySelector(".discount").value) || 0;
            const taxRate = parseFloat(row.querySelector(".tax-rate").value) || 0;

            const taxableAmount = qty * (priceBeforeTax - discount);
            totalBeforeTax += qty * priceBeforeTax;
            totalDiscount += qty * discount;

            if (!taxSummary[taxRate]) {
                taxSummary[taxRate] = { taxableAmount: 0, sgst: 0, cgst: 0, igst: 0 };
            }

            taxSummary[taxRate].taxableAmount += taxableAmount;
        });

        // Adjust taxable amounts based on Other Discounts
        const otherDiscount = parseFloat(otherDiscountInput.value) || 0;
        const discountRatio = otherDiscount / totalBeforeTax || 0;

        Object.keys(taxSummary).forEach(taxRate => {
            const adjustedTaxableAmount = taxSummary[taxRate].taxableAmount * (1 - discountRatio);
            if (placeOfSupplyDropdown.value === clientPlaceOfSupply) {
                // Calculate SGST & CGST
                const halfRate = taxRate / 2;
                taxSummary[taxRate].sgst = adjustedTaxableAmount * (halfRate / 100);
                taxSummary[taxRate].cgst = adjustedTaxableAmount * (halfRate / 100);
				taxSummary[taxRate].taxableAmount = adjustedTaxableAmount;
            } else {
                // Calculate IGST
                taxSummary[taxRate].igst = adjustedTaxableAmount * (taxRate / 100);
				taxSummary[taxRate].taxableAmount = adjustedTaxableAmount;
            }
        });

        // Update the summary section
        updateSummary(totalBeforeTax, totalDiscount, otherDiscount, taxSummary);
		calculateTotalPayable(taxSummary);
    }

    // Update Summary Section
    function updateSummary(totalBeforeTax, totalDiscount, otherDiscount, taxSummary) {
        summarySection.innerHTML = `
            <h3>Summary</h3>
            <p>Total Before Tax: ₹${totalBeforeTax.toFixed(2)}</p>
            <p>Total Discount: ₹${totalDiscount.toFixed(2)}</p>
            <p>Other Discount: ₹${otherDiscount.toFixed(2)}</p>
            <table border="1">
                <tr>
                    <th>Tax Rate</th>
                    <th>Taxable Amount</th>
                    <th>SGST</th>
                    <th>CGST</th>
                    <th>IGST</th>
                </tr>
                ${Object.entries(taxSummary).map(([taxRate, values]) => `
                    <tr>
                        <td>${taxRate}%</td>
                        <td>₹${values.taxableAmount.toFixed(2)}</td>
                        <td>₹${values.sgst.toFixed(2)}</td>
                        <td>₹${values.cgst.toFixed(2)}</td>
                        <td>₹${values.igst.toFixed(2)}</td>
                    </tr>
                `).join("")}
            </table>
        `;
    }
	
	function calculateTotalPayable(taxSummary) {
		console.log("Starting calculateTotalPayable function...");
		let totalPayable = 0;

		Object.values(taxSummary).forEach(({ taxableAmount, sgst, cgst, igst }) => {
			totalPayable += taxableAmount + (sgst || 0) + (cgst || 0) + (igst || 0);
			console.log("Processing tax slab:", { taxableAmount, sgst, cgst, igst });
		});
		console.log("Calculated Total Payable:", totalPayable);

		const totalPayableElement = document.getElementById("totalPayable");
		const totalInWordsElement = document.getElementById("totalPayableWords");
		console.log("Total Payable Element:", totalPayableElement);
		console.log("Total In Words Element:", totalInWordsElement);

		if (totalPayableElement && totalInWordsElement) {
			totalPayableElement.innerText = `Total Payable: ₹${totalPayable.toFixed(2)}`;
			totalInWordsElement.innerText = `In Words: ${convertNumberToWords(totalPayable)} Rupees Only`;
		} else {
			console.error("Total Payable or Words element is missing.");
		}
	}

// Function to convert numbers to words (basic implementation)
	function convertNumberToWords(number) {
		const words = [
			'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
			'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen',
			'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety', 'Hundred', 'Thousand', 'Lakh'
		];

		if (number === 0) return words[0];
		let inWords = '';

		const convert = (num) => {
			if (num < 20) return words[num];
			else if (num < 100) return words[18 + Math.floor(num / 10)] + (num % 10 !== 0 ? ' ' + words[num % 10] : '');
			else if (num < 1000) return words[Math.floor(num / 100)] + ' ' + words[28] + (num % 100 !== 0 ? ' and ' + convert(num % 100) : '');
			else if (num < 100000) return convert(Math.floor(num / 1000)) + ' ' + words[29] + (num % 1000 !== 0 ? ' ' + convert(num % 1000) : '');
			else return convert(Math.floor(num / 100000)) + ' ' + words[30] + (num % 100000 !== 0 ? ' ' + convert(num % 100000) : '');
		};

		inWords = convert(Math.floor(number));
		const decimalPart = Math.round((number % 1) * 100);
		if (decimalPart > 0) inWords += ' and ' + convert(decimalPart) + ' Paise';
		return inWords;
	}


    // Event Listeners
    placeOfSupplyDropdown.addEventListener("change", calculateTaxes);
    otherDiscountInput.addEventListener("input", calculateTaxes);

    fetchClientPlaceOfSupply();
	
	const calculateButton = document.createElement("button");
    calculateButton.innerText = "Calculate";
    calculateButton.type = "button";
    calculateButton.onclick = () => calculateTaxes();
    document.getElementById("billingDetailsForm").appendChild(calculateButton);
});


