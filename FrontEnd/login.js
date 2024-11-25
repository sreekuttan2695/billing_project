// Login functionality
document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("http://127.0.0.1:8000/api/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password }),
            credentials: "include"
        });

        const data = await response.json();

        if (response.ok) {
            alert("Login successful! JWT tokens are stored in HttpOnly cookies.");
        } else {
            alert("Login failed: " + (data.message || "An error occurred"));
        }
    } catch (error) {
        console.error("Error during login:", error);
    }
});

// Protected view access functionality
document.getElementById("protectedViewButton").addEventListener("click", async function () {
    try {
        const response = await fetch("http://127.0.0.1:8000/protected/", {
            method: "GET",
            credentials: "include"
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById("protectedViewResult").innerText = "Protected View Response: " + JSON.stringify(data);
        } else {
            document.getElementById("protectedViewResult").innerText = "Failed to access protected view.";
        }
    } catch (error) {
        console.error("Error accessing protected view:", error);
    }
});

// User creation functionality
document.getElementById("createUserForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const newUsername = document.getElementById("newUsername").value;
    const newPassword = document.getElementById("newPassword").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;
    const address = document.getElementById("address").value;
    const clientId = document.getElementById("userClientId").value; // Updated to "userClientId"

    try {
        const response = await fetch("http://127.0.0.1:8000/api/create-user/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username: newUsername, password: newPassword, email, phone, address, client_id: clientId }),
            credentials: "include"
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById("result").innerText = "User created successfully!";
        } else {
            document.getElementById("result").innerText = "Error creating user: " + (data.message || JSON.stringify(data));
        }
    } catch (error) {
        console.error("Error creating user:", error);
    }
});

// Client creation functionality
document.getElementById("createClientForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const clientId = document.getElementById("clientId").value;  // Updated to match unique "clientId" for Create Client
    const clientName = document.getElementById("clientName").value;
    const clientAddress = document.getElementById("clientAddress").value;
    const clientPhone = document.getElementById("clientPhone").value;
    const clientEmail = document.getElementById("clientEmail").value;
    const createdBy = document.getElementById("createdBy").value;
    const lastUpdatedBy = document.getElementById("lastUpdatedBy").value;

    console.log("Client ID:", clientId);  // Debugging

    try {
        const response = await fetch("http://127.0.0.1:8000/api/create-client/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                client_id: clientId,
                name: clientName,
                address: clientAddress,
                phone: clientPhone,
                email: clientEmail,
                created_by: createdBy,
                last_updated_by: lastUpdatedBy
            }),
            credentials: "include"
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById("result").innerText = "Client created successfully!";
        } else {
            document.getElementById("result").innerText = "Error creating client: " + (data.message || JSON.stringify(data));
        }
    } catch (error) {
        console.error("Error creating client:", error);
    }
});

document.getElementById("logoutButton").addEventListener("click", async function () {
    try {
        const response = await fetch("http://127.0.0.1:8000/api/logout/", {
            method: "POST",
            credentials: "include"
        });

        if (response.ok) {
            alert("Logout successful!");
        } else {
            const data = await response.json();
            console.error("Failed to log out:", data);
            alert("Logout failed: " + (data.message || "An error occurred"));
        }
    } catch (error) {
        console.error("Error during logout:", error);
    }
});
