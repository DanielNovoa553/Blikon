// Obtener el formulario y asignar el evento 'submit'
document.querySelector('form').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevenir el comportamiento por defecto (recargar la página)

    const email = document.querySelector('#email').value;
    const password = document.querySelector('#password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST', // Cambiar a POST
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Si la respuesta es exitosa
            console.log('Login exitoso', data);
            alert('Inicio de sesión exitoso');
        } else {
            // Si la respuesta contiene un error
            console.log('Error:', data);
            alert(data.error || 'Hubo un error en el inicio de sesión');
        }
    } catch (error) {
        console.log('Error:', error);
        alert('Ocurrió un error al intentar iniciar sesión');
    }
});
