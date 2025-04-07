# API - Sistema de Suscripciones y Usuarios

## Descripción

Este sistema permite gestionar usuarios, suscripciones y autenticación mediante tokens JWT. Los usuarios pueden registrarse, iniciar sesión, y suscribirse a planes premium o básicos. Los administradores pueden consultar y modificar el estado de suscripciones.

---

## Endpoints

### POST /login/adduser

Crea un nuevo usuario en la base de datos si no existe un usuario con el mismo email o teléfono.

#### Requiere token JWT válido como parámetro en la URL (`?token=...`).

#### 📥 JSON de entrada:
```json
{
  "nombres": "Juan",
  "apellidos": "Pérez",
  "email": "juan@example.com",
  "password": "123456",
  "tipo": "ADMIN",
  "telefono": "5512345678"
}
📤 JSON de salida (éxito):

{
  "message": "Se creo el usuario exitosamente",
  "response": true
}
📤 JSON de salida (error - email ya registrado):

{
  "message": "ERROR se encontro una cuenta registrada con el correo electronico proporcionado"
}
📤 JSON de salida (error - teléfono ya registrado):

{
  "message": "ERROR Se encontro una cuenta registrada con el telefono proporcionado"
}
POST /login
Inicia sesión con email y contraseña y genera un token JWT.

📥 JSON de entrada:

{
  "email": "juan@example.com",
  "password": "123456"
}
📤 JSON de salida (éxito):

{
  "token": "jwt_token_value",
  "status": "Inicio de sesión exitoso.",
  "message": "Token generado exitosamente.",
  "expiration_time": "07-04-2025 12:30:00"
}
📤 JSON de salida (error - credenciales inválidas):

{
  "error": "Credenciales invalidas."
}
POST /update_subscription_status
Actualiza o cancela la suscripción de un usuario según el id del usuario proporcionado.

Requiere token JWT válido como parámetro en la URL (?token=...).
Parámetros:
id_usuario (int): El ID del usuario cuya suscripción se va a actualizar.

estado_suscripcion (boolean): true para activar la suscripción, false para cancelarla.

📥 JSON de entrada:

{
  "estado_suscripcion": true
}
📤 JSON de salida (éxito):

{
  "message": "La suscripción fue activada exitosamente.",
  "response": true
}
📤 JSON de salida (error - usuario no encontrado):

{
  "message": "El usuario con el ID proporcionado no existe.",
  "response": false
}
📤 JSON de salida (error - actualización fallida):

{
  "message": "Ocurrió un error al actualizar el estado de la suscripción.",
  "response": false
}
GET /get_subscription_status
Consulta el estado de la suscripción de un usuario por su id.

Requiere token JWT válido como parámetro en la URL (?token=...).
Parámetros:
id_usuario (int): El ID del usuario.

📤 JSON de salida (éxito):

{
  "estado_suscripcion": true,
  "message": "Estado de suscripción consultado exitosamente."
}
📤 JSON de salida (error - usuario no encontrado):

{
  "message": "El usuario con el ID proporcionado no existe.",
  "response": false
}
Ejemplo de uso
1. Registrar un usuario
POST /login/adduser

Para crear un nuevo usuario, realiza una solicitud POST al endpoint /login/adduser con un JSON en el cuerpo de la solicitud que contenga los datos del usuario.

Ejemplo de JSON de entrada:

{
  "nombres": "Juan",
  "apellidos": "Pérez",
  "email": "juan@example.com",
  "password": "123456",
  "tipo": "ADMIN",
  "telefono": "5512345678"
}
2. Iniciar sesión
POST /login

Para iniciar sesión, se debe enviar un email y una contraseña válidos. El sistema generará un token JWT que puede ser usado para realizar otras operaciones en la API.

Ejemplo de JSON de entrada:

{
  "email": "juan@example.com",
  "password": "123456"
}
Ejemplo de JSON de salida:

{
  "token": "jwt_token_value",
  "status": "Inicio de sesión exitoso.",
  "message": "Token generado exitosamente.",
  "expiration_time": "07-04-2025 12:30:00"
}
3. Consultar el estado de la suscripción
GET /get_subscription_status

Para obtener el estado de la suscripción de un usuario, se debe enviar el id_usuario y el token JWT en la URL.

Ejemplo de JSON de salida:

{
  "estado_suscripcion": true,
  "message": "Estado de suscripción consultado exitosamente."
}
4. Actualizar o cancelar la suscripción
POST /update_subscription_status

Para actualizar o cancelar la suscripción de un usuario, se debe enviar el id_usuario y el nuevo estado de la suscripción (activa o cancelada).

Ejemplo de JSON de entrada:

{
  "estado_suscripcion": true
}
Errores comunes
Token inválido o ausente: Cuando no se proporciona un token válido.

{
  "error": "Token InvalidoO."
}
Credenciales incorrectas: Si el email o la contraseña no son correctos.
{
  "error": "Credenciales invalidas."
}
Campos faltantes o inválidos: Si falta algún campo necesario en el cuerpo de la solicitud.
{
  "error": "Usuario o contraseña incorrectos."
}
