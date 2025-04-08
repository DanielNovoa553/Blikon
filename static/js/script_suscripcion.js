document.addEventListener("DOMContentLoaded", function() {
    const token = localStorage.getItem("token");
    const email = localStorage.getItem("email");


    if (!token) {
        alert("No token found. Please log in again.");
        window.location.href = "/login_form";  // Redirigir a login si no hay token
        return;
    }

    fetch(`/get_suscripcion_usuario?email=${encodeURIComponent(email)}`, {
        method: 'GET',
        headers: {
            'Authorization': token  // Envía el token en el encabezado Authorization

        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            // Aquí puedes actualizar la página con los detalles del usuario
            document.getElementById('nombres').textContent = data.nombres;
            document.getElementById('apellidos').textContent = data.apellidos;
            document.getElementById('email').textContent = data.email;
            document.getElementById('telefono').textContent = data.telefono;
            document.getElementById('tipo').textContent = data.tipo;
            if (data.estado_suscripcion === "True") {
                document.getElementById('estado_suscripcion').textContent = "Activa";
            }
            else {
                document.getElementById('estado_suscripcion').textContent = "Cancelada";
            }
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
});
