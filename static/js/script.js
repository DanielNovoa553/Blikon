 document.getElementById("loginForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const hashedPassword = CryptoJS.MD5(password).toString(CryptoJS.enc.Hex);

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email, password: hashedPassword })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta del backend:", data);
        if (data.token) {
            localStorage.setItem("token", data.token);
            localStorage.setItem("email", data.email);
            alert("Inicio de sesión exitoso");

            //enviar a la pagina para ver la suscripcion
            window.location.href = '/suscripcion_usuario';


        } else {
            alert("Error de inicio de sesión: " + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});