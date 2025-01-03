document.getElementById("registerForm").addEventListener("submit", function(event) {
    event.preventDefault();
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email, password: password }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("message").innerText = data.message;
        if (data.status === "success") {
            // Reset form or redirect user as needed
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});