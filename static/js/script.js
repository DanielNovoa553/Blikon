document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    alert(email + " " + password)


    const formData = {
        email: email,
        password: password
    };


    fetch('/login_form', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {

        document.getElementById('message').textContent = data.message || 'Error al iniciar sesión';
    })
    .catch(error => {

        console.error('Error:', error);
        document.getElementById('message').textContent = 'Ocurrió un error al enviar los datos';
    });
});
