document.getElementById("encrypt-btn").addEventListener("click", async function() {
    const file = document.getElementById("file-upload").files[0];
    const password = document.getElementById("password").value;

    if (!file) {
        showMessage("Please select a file to encrypt.");
        return;
    }

    if (!password) {
        showMessage("Please enter a password.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("password", password);

    try {
        const response = await fetch("/encrypt/", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        if (response.ok) {
            showMessage(`File encrypted successfully: ${result.encrypted_file}`);
        } else {
            showMessage(`Error: ${result.detail}`);
        }
    } catch (error) {
        console.log(error);
        showMessage("Error during encryption.");
    }
});

document.getElementById("decrypt-btn").addEventListener("click", async function() {
    const file = document.getElementById("file-upload-decrypt").files[0];
    const password = document.getElementById("password-decrypt").value;

    if (!file) {
        showMessage("Please select a file to decrypt.");
        return;
    }

    if (!password) {
        showMessage("Please enter a password.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("password", password);

    try {
        const response = await fetch("http://127.0.0.1:8000/decrypt/", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        if (response.ok) {
            showMessage(`File decrypted successfully: ${result.decrypted_file}`);
        } else {
            showMessage(`Error: ${result.detail}`);
        }
    } catch (error) {
        showMessage("Error during decryption.");
    }
});

// Function to display messages
function showMessage(message) {
    document.getElementById("status-message").textContent = message;
}

// Password visibility toggle for encryption and decryption
document.getElementById("toggle-eye").addEventListener("click", function () {
    const passwordField = document.getElementById("password");
    const icon = this;

    if (passwordField.type === "password") {
        passwordField.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        passwordField.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
});

document.getElementById("toggle-eye-decrypt").addEventListener("click", function () {
    const passwordField = document.getElementById("password-decrypt");
    const icon = this;

    if (passwordField.type === "password") {
        passwordField.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        passwordField.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
});

// Search functionality for decrypted files
document.getElementById("search-btn").addEventListener("click", function () {
    const searchTerm = document.getElementById("search-file").value.trim();
    if (searchTerm) {
        showMessage(`Searching for decrypted files containing: ${searchTerm}`);
    } else {
        showMessage("Please enter a search term.");
    }
});
