from datetime import datetime
from db_data import connectdb
import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
from flask_cors import CORS, cross_origin
import jwt
import hashlib


app = Flask(__name__)
app.config['SECRET_KEY'] = '3643dcdf2beb1ace0f0dd02019e9bee9'
CORS(app, support_credentials=True)

'#-------------------------------------------------Funciones--------------------------------------------------------'


def validateJson(inputIn, field):
    """
        Valida la existencia y contenido de un campo en un JSON de entrada.

        Args:
            inputIn (dict): Diccionario que representa el JSON de entrada.
            field (str): Nombre del campo a validar dentro del JSON.

        Returns:
            str | list | int | bool | Any | bool:
                - El valor del campo si existe y no está vacío.
                - `False` si el campo no existe o está vacío ('').

        Notas:
            - Si el campo es booleano, se convierte a string antes de devolverlo.
            - Si es lista, string o número entero, se devuelve tal cual.
            - Para cualquier otro tipo de dato, también se retorna como está.
        """
    print('Se valida el campo -> ' + field)
    if inputIn and field in inputIn:
        print(inputIn[field])
        print(type(inputIn[field]))
        if inputIn[field] == '':
            return False
        else:
            if type(inputIn[field]) == bool:
                print('El campo es un booleano')
                return str(inputIn[field])
            if type(inputIn[field]) == list:
                print('El campo es una lista')
                return inputIn[field]
            if type(inputIn[field]) == str:
                print('El campo es un string')
                return inputIn[field]
            if type(inputIn[field]) == int:
                print('El campo es un numero')
                return inputIn[field]
            else:
                return inputIn[field]
    else:
        return False

def getInput(inputIn):
    """
        Convierte el valor de entrada a una cadena de texto.

        Args:
            inputIn (Any): Valor que se desea convertir a cadena.

        Returns:
            str | bool:
                - Si `inputIn` no es falso, devuelve el valor como una cadena de texto.
                - Si `inputIn` es `False`, devuelve `False`.

        Notas:
            - Esta función asegura que cualquier valor distinto de `False` sea convertido a string.
        """
    if inputIn == False:
        return False
    else:
        return str(inputIn)


@app.route('/')
def index():
    """
    Redirige a la página de inicio de sesión si el usuario no está autenticado.

    Esta ruta maneja las solicitudes a la raíz del sitio ('/'). Si un usuario accede a la raíz
    sin estar autenticado, será redirigido automáticamente a la página de inicio de sesión.

    Returns:
        Response: La redirección a la ruta de inicio de sesión si el usuario no está autenticado.
    """
    return redirect(url_for('login_form'))



def generate_token():
    """
    Genera un token de acceso JWT con expiración.

    Returns:
        tuple:
            - token (str): Token JWT codificado usando HS256.
            - expiration_time_mexico (datetime): Fecha y hora de expiración del token en la zona horaria de Ciudad de México.

    Notas:
        - El token expira en 60 minutos a partir del momento de su creación.
        - El payload incluye:
            - 'exp': Tiempo de expiración en UTC.
            - 'iat': Tiempo en que se generó el token (Issued At).
        - Se utiliza la clave secreta configurada en `app.config['SECRET_KEY']`.
    """
    time = datetime.datetime.now(tz=datetime.timezone.utc)
    plus_time = datetime.timedelta(minutes=60)
    expiration_time_mexico = datetime.datetime.now() + plus_time
    print(f"plus_time: {plus_time}")
    expiration_time = time + plus_time
    print(f"expiration_time: {expiration_time_mexico}")
    payload = {'exp': expiration_time, 'iat': datetime.datetime.now(tz=datetime.timezone.utc)}
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token, expiration_time_mexico


def verify_token(token):
    """
    Verifica y decodifica un token JWT.

    Args:
        token (str): Token JWT que se desea verificar.

    Returns:
        dict:
            - Si el token es válido, retorna el payload (contenido del token).
            - Si el token ha expirado, retorna:
                {
                    'error': 'Token a expirado.',
                    'status': False
                }
            - Si el token es inválido, retorna:
                {
                    'error': 'Token InvalidoO.'
                }

    Raises:
        jwt.ExpiredSignatureError: Cuando el token ha expirado.
        jwt.InvalidTokenError: Cuando el token es inválido.

    Notas:
        - El token debe estar firmado con la misma clave secreta definida en `app.config['SECRET_KEY']`.
        - El algoritmo utilizado debe ser 'HS256'.
    """
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token a expirado.',
                'status': False}
    except jwt.InvalidTokenError:
        return {'error': 'Token InvalidoO.'}


@app.route('/login', methods=['POST'], strict_slashes=False, endpoint='login')
def login():
    """
    Inicia sesión y genera un token JWT si las credenciales del usuario son válidas.

    Requiere:
        - email (str): Correo electrónico del usuario (en el cuerpo JSON).
        - password (str): Contraseña del usuario (en el cuerpo JSON).

    Returns:
        JSON:
            - 200 OK: Si las credenciales son válidas, retorna:
                {
                    "token": <str>,
                    "status": "Inicio de sesión exitoso.",
                    "message": "Token generado exitosamente.",
                    "expiration_time": "dd-mm-YYYY HH:MM:SS" (hora de expiración en horario de Ciudad de México)
                }
            - 400/401:
                - Si falta el email o la contraseña.
                - Si las credenciales son inválidas.
            - 500:
                - Si ocurre un error al consultar la base de datos.

    Notas:
        - La contraseña no se cifra en esta función, se compara directamente. Se recomienda aplicar hash (por ejemplo, MD5 o SHA256).
        - El token se genera mediante la función `generate_token()`.
    """
    print('endpoint login alzanzado')
    connection = connectdb()
    if isinstance(connection, Exception):
        return jsonify({'Error al conectar con la base de datos, detalle: ': str(connection)})

    else:
        cursor = connection.cursor()
        # json validation
        email = request.json.get('email')
        password = request.json.get('password')
        if not email or not password:
            return jsonify({'error': 'Usuario o contraseña incorrectos.'})
        else:
            try:
                sql = f"SELECT * FROM usuario WHERE email = '{email}' AND password = '{password}'"
                cursor.execute(sql)
                result = cursor.fetchone()
                if result:
                    token = generate_token()
                    expiration_time_mexico = token[1].strftime("%d-%m-%Y %H:%M:%S")
                    connection.close()
                    cursor.close()
                    return jsonify({'token': token[0],
                                    'status': 'Inicio de sesión exitoso.',
                                    'message': 'Token generado exitosamente.',
                                    'expiration_time': expiration_time_mexico,
                                    'email': email})
                else:
                    connection.close()
                    cursor.close()

                    return jsonify({'error': 'Credenciales invalidas.'})

            except Exception as e:
                connection.close()
                cursor.close()
                return jsonify({'error': str(e)})


'#---------------------------------------------------Crear Usuario----------------------------------------------------'


@app.route('/login/adduser', methods=['POST'])
@cross_origin(supports_credentials=True)
def adduser():
    """
        Crea un nuevo usuario en la base de datos si no existe un usuario con el mismo email o telefono.

        Requiere un token JWT válido como parámetro en la URL (?token=...).

        El cuerpo de la solicitud debe estar en formato JSON y contener los siguientes campos:
            - nombres (str): Nombres del usuario.
            - apellidos (str): Apellidos del usuario.
            - email (str): Correo electrónico del usuario.
            - password (str): Contraseña sin cifrar (se cifrará con MD5).
            - tipo (str): Tipo de usuario.
            - telefono (str): Número de teléfono.

        Returns:
            JSON:
                - 200 OK si el usuario fue creado exitosamente.
                - 400 Bad Request si faltan campos o el JSON está malformado.
                - 401 Unauthorized si el email o el teléfono ya están registrados.
                - 500 Internal Server Error si ocurre un error en el proceso.

        Ejemplo de cuerpo JSON:
        {
            "nombres": "Juan",
            "apellidos": "Pérez",
            "email": "juan@example.com",
            "password": "123456",
            "tipo": "ADMIN",
            "telefono": "5512345678"
        }
        """
    print('adduser')
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Token is missing.'})

    payload = verify_token(token)
    if 'error' in payload:
        return jsonify(payload)
    json_out = {}
    json_out["response"] = False
    output = {'response': False}

    inputIn = request.get_json(silent=True)

    print('Se valida JSON de entrada')
    print(inputIn)
    if inputIn is not None:
        print('Hay un JSON de entrada')
        # Nombres
        nombres = getInput(validateJson(inputIn, 'nombres')).upper()
        if nombres == False:
            output['nombres'] = 'No se proporciono el campo o esta vacio'
            return jsonify(output), 400

        # Apellidos
        apellidos = getInput(validateJson(inputIn, 'apellidos')).upper()
        if apellidos == False:
            output['apellidos'] = 'No se proporciono el campo o esta vacio'
            return jsonify(output), 400

        # Email
        email = getInput(validateJson(inputIn, 'email')).lower()
        if email == False:
            output['email'] = 'No se proporciono el campo o esta vacio'
            return jsonify(output), 400

        # Password
        if request.json is None:
            json_out["error"] = "No se envio body en la solicitud"
            return json_out, 400
        else:
            content = request.json
            pass

        if 'password' in content:
            print("pasa password")
            password = content["password"]
            pass
        else:
            json_out["error"] = "No se envio el password"
            return json_out, 500

        hash_object = hashlib.md5(password.encode())
        md5_hash = hash_object.hexdigest()
        print('Clave Encriptada', md5_hash)

        # Tipo
        tipo = getInput(validateJson(inputIn, 'tipo')).upper()
        if tipo == False:
            output['tipo'] = 'No se proporciono el campo o esta vacio'
            return jsonify(output), 400

        # Telefono
        telefono = getInput(validateJson(inputIn, 'telefono'))
        if telefono == False:
            output['telefono'] = 'No se proporciono el campo o esta vacio'
            return jsonify(output), 400


    else:
        print('No se proporciono JSON')
        output['body'] = 'No se proporciono body'
        return jsonify(output), 400

    connection = connectdb()
    if isinstance(connection, Exception):
        return jsonify({'error': 'Error al conectar con la base de datos'}), 500

    cur = connection.cursor()
    try:

        print('Se obtiene la informacion propocionada para validar no exista la cuenta')
        query = f"select * from usuario where email = '{str(email)}'"
        print(query)
        cur.execute(query)
        usuarioEmail = cur.fetchone()
        if usuarioEmail is not None:
            print('ERROR se encontro una cuenta registrada con el correo electronico proporcionado')
            output['message'] = 'ERROR se encontro una cuenta registrada con el correo electronico proporcionado'
            return jsonify(output), 401

        else:
            print('No se encontro una cuenta registrada con email, validar telefono')
            query = f"select * from usuario where telefono = '{str(telefono)}'"
            print(query)
            cur.execute(query)
            usuarioTelefono = cur.fetchone()

            if usuarioTelefono is not None:
                print(' ERROR se encontro una cuenta registrada con el telefono proporcionado')
                output['message'] = 'ERROR Se encontro una cuenta registrada con el telefono proporcionado'
                return jsonify(output), 401

            else:
                print('No se encontro el telefono en la BD, se procede a crear cuenta')
                fecha_hoy = datetime.datetime.today().strftime('%Y-%m-%d %H:%M')
                print('Se hace insert a la tabla usuario para crear el usuario')
                cur = connection.cursor()
                query = f"insert into usuario values (default, '{nombres}', '{apellidos}', '{email}'," \
                        f"'{md5_hash}', '{tipo}', '{telefono}', '{fecha_hoy}' ,true)"
                print(query)
                cur.execute(query)

    except Exception as e:
        print(e)
        print('Ocurrio un error al crear al usuario en la BD')
        output['message'] = 'Ocurrio un error al crear al usuario en la BD' + str(e)
        return jsonify(output), 500

    output['message'] = 'Se creo el usuario exitosamente'
    output['response'] = True

    connection.commit()
    cur.close()
    connection.close()
    print('Ejecucion correcta')
    return jsonify(output), 200



@app.route('/login/suscribir', methods=['POST'])
@cross_origin(supports_credentials=True)
def suscribir():
    """
    Endpoint para suscribir a un usuario a un plan (premium o básico).
    Requiere un token JWT válido como parámetro en la URL (?token=...).

    El cuerpo de la solicitud debe estar en formato JSON y contener:
        - email (str): Correo electrónico del usuario.
        - plan (str): Nombre del plan, puede ser "premium" o "basico".

    Returns:
        JSON:
            - 200 OK si la suscripción fue exitosa.
            - 400 Bad Request si faltan campos.
            - 401 Unauthorized si el usuario no existe o el token es inválido.
            - 500 Internal Server Error si ocurre un error.
    """
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Token is missing.'}), 401

    payload = verify_token(token)
    if 'error' in payload:
        return jsonify(payload), 401

    inputIn = request.get_json(silent=True)
    if inputIn is None:
        return jsonify({'error': 'No se proporciono body'}), 400

    # Validar email
    email = getInput(validateJson(inputIn, 'email')).lower()
    if email == False:
        return jsonify({'email': 'No se proporciono el campo o esta vacio'}), 400

    # Validar plan
    plan = getInput(validateJson(inputIn, 'plan')).upper()
    if plan == False:
        return jsonify({'plan': 'No se proporciono el campo o esta vacio'}), 400

    if plan not in ['PREMIUM', 'BASICO']:
        return jsonify({'plan': 'El plan debe ser "premium" o "basico"'}), 400

    # Verificar usuario en base de datos
    connection = connectdb()
    if isinstance(connection, Exception):
        return jsonify({'error': 'Error al conectar con la base de datos'}), 500

    try:
        cur = connection.cursor()
        query = f"SELECT * FROM usuario WHERE email = '{email}'"
        cur.execute(query)
        usuario = cur.fetchone()
        if usuario is None:
            return jsonify({'error': 'El usuario no existe'}), 401

        # Actualizar suscripción
        estado_suscripcion = True
        update_query = f"UPDATE usuario SET tipo = '{plan}', estado_suscripcion = {estado_suscripcion} WHERE email = '{email}'"
        cur.execute(update_query)
        connection.commit()
        cur.close()
        connection.close()

        return jsonify({'message': f'Suscripcion al plan {plan} realizada con exito'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/login/estado_suscripcion', methods=['POST'])
@cross_origin(supports_credentials=True)
def estado_suscripcion():
    """
    Endpoint para consultar el estado de suscripción de un usuario.
    Requiere un token JWT válido como parámetro en la URL (?token=...).

    El cuerpo de la solicitud debe estar en formato JSON y contener:
        - email (str): Correo electrónico del usuario.

    Returns:
        JSON:
            - 200 OK con el estado de la suscripción.
            - 400 Bad Request si falta el campo.
            - 401 Unauthorized si el token es inválido o el usuario no existe.
            - 500 Internal Server Error si ocurre un error.
    """
    print('estado_suscripcion')
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Token is missing.'}), 401

    payload = verify_token(token)
    if 'error' in payload:
        return jsonify(payload), 401

    output = {'response': False}
    inputIn = request.get_json(silent=True)

    if inputIn is None:
        output['body'] = 'No se proporciono body'
        return jsonify(output), 400

    # Validar email
    email = getInput(validateJson(inputIn, 'email')).lower()
    if email == False:
        output['email'] = 'No se proporciono el campo o esta vacio'
        return jsonify(output), 400

    connection = connectdb()
    if isinstance(connection, Exception):
        return jsonify({'error': 'Error al conectar con la base de datos'}), 500

    try:
        cur = connection.cursor()

        # Verificar existencia del usuario y estado
        print('Consultando estado de suscripcion')
        query = f"SELECT estado_suscripcion, tipo FROM usuario WHERE email = '{email}'"
        print(query)
        cur.execute(query)
        resultado = cur.fetchone()

        if resultado is None:
            output['message'] = 'El usuario no existe'
            return jsonify(output), 401

        estado = resultado[0]  # True o False
        if estado == True:
            output['estado_suscripcion'] = 'Activa'
        else:
            output['estado_suscripcion'] = 'Inactiva'
        tipo = resultado[1]  # PREMIUM o BASICO
        output['tipo'] = tipo
        output['message'] = 'Consulta exitosa'
        output['response'] = True
        output['Usuario'] = email
        print('Ejecucion correcta')
        cur.close()
        connection.close()
        return jsonify(output), 200

    except Exception as e:
        print(e)
        output['message'] = 'Ocurrio un error al consultar el estado de suscripcion ' +str(e)
        return jsonify(output), 500


@app.route('/login/actualizar_suscripcion/<int:id>', methods=['POST'])
@cross_origin(supports_credentials=True)
def actualizar_suscripcion(id):
    """
    Actualiza el tipo de suscripcion o cancela la suscripcion de un usuario.
    Requiere token JWT valido como parametro (?token=...).

    Parametros:
        - id (int): ID del usuario.

    Body JSON:
        {
            "accion": "cancelar" o "actualizar",
            "tipo_suscripcion": "premium" o "basico" (solo si accion es "actualizar")
        }

    Returns:
        JSON con resultado de la operacion.
    """
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Token is missing.'}), 401

    payload = verify_token(token)
    if 'error' in payload:
        return jsonify(payload), 401

    inputIn = request.get_json(silent=True)
    if not inputIn:
        return jsonify({'error': 'No se envio body en la solicitud'}), 400

    accion = inputIn.get('accion').upper()
    tipo_suscripcion = inputIn.get('tipo_suscripcion', '').upper()

    if not accion:
        return jsonify({'error': 'No se proporciono la accion'}), 400

    connection = connectdb()
    if isinstance(connection, Exception):
        return jsonify({'error': 'Error al conectar con la base de datos'}), 500

    try:
        cur = connection.cursor()

        # Validar que el usuario exista
        cur.execute(f"SELECT id FROM usuario WHERE id = {id}")
        usuario = cur.fetchone()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 400

        if accion == 'CANCELAR':
            cur.execute(f"""
                UPDATE usuario 
                SET estado_suscripcion = false 
                WHERE id = {id}
            """)
            mensaje = 'Suscripcion cancelada exitosamente'

        elif accion == 'ACTUALIZAR':
            if tipo_suscripcion not in ['PREMIUM', 'BASICO']:
                return jsonify({'error': 'Tipo de suscripcion invalido'}), 400

            cur.execute(f"""
                UPDATE usuario 
                SET estado_suscripcion = true, tipo = '{tipo_suscripcion}' 
                WHERE id = {id}
            """)
            mensaje = f'Suscripcion actualizada a {tipo_suscripcion}'

        else:
            return jsonify({'error': 'Accion invalida, debe ser "cancelar" o "actualizar"'}), 400

        connection.commit()
        cur.close()
        connection.close()
        return jsonify({'message': mensaje, 'response': True}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'Error al actualizar suscripcion' + str(e)}), 500




@app.route('/login_form', methods=['GET'])
def login_form():
    """
    Renderiza el formulario de inicio de sesión.

    Esta ruta sirve para mostrar el formulario que permite al usuario autenticarse.
    Se incluyen cabeceras para evitar que la página sea almacenada en caché, previniendo
    que el usuario pueda volver a páginas protegidas luego de cerrar sesión usando el botón "atrás".

    Returns:
        Response: El contenido HTML del formulario de login.
    """
    response = make_response(render_template('login_form.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response




@app.route('/suscripcion_usuario', methods=['GET'])
def suscripcion_usuario():
    """
    Renderiza la página de detalles de la suscripción del usuario.

    Esta ruta se utiliza para mostrar los detalles de la suscripción de un usuario que ha iniciado sesión.
    Cuando se hace una solicitud GET a esta ruta, se devuelve el archivo
    'suscripcion_usuario.html', que contiene la información relevante sobre la suscripción del usuario,
    como nombres, apellidos, email, teléfono, tipo y estado de suscripción.

    Se agregan cabeceras para evitar el almacenamiento en caché por parte del navegador,
    previniendo que los datos permanezcan visibles tras cerrar sesión o navegar hacia atrás.

    Returns:
        Response: El contenido HTML de la página con los detalles de la suscripción del usuario.
    """
    response = make_response(render_template('suscripcion_usuario.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response



@app.route('/get_suscripcion_usuario', methods=['GET'])
def get_suscripcion_usuario():
    """
    Obtiene los detalles de la suscripción de un usuario a partir de su correo electrónico.

    Esta ruta es utilizada para recuperar la información detallada de la suscripción de un usuario.
    El correo electrónico del usuario se pasa como un parámetro de consulta en la solicitud GET, y se
    utiliza junto con el token de autorización para verificar la identidad del usuario y recuperar
    sus detalles desde la base de datos.

    Se devuelve la información del usuario, como nombres, apellidos, email, teléfono, tipo y estado de
    la suscripción. Si no se encuentra al usuario o hay algún error, se devuelve un mensaje de error.

    Returns:
        Response: Un objeto JSON con los detalles de la suscripción del usuario si se encuentra, o un
                  mensaje de error si no se encuentra o si ocurre un problema en la conexión.

    Raises:
        403: Si no se proporciona un token de autorización.
        401: Si el token de autorización ha expirado o es inválido.
        500: Si ocurre un error al conectar con la base de datos.
        404: Si no se encuentra un usuario con el correo proporcionado.
    """
    token = request.args.get('token')
    email = request.args.get('email')

    if not token:
        return jsonify({'error': 'Token is missing!'}), 403

    payload = verify_token(token)
    if 'error' in payload:
        return jsonify(payload), 401

    try:
        # Consultar los detalles del usuario por email
        connection = connectdb()
        if isinstance(connection, Exception):
            return jsonify({'error': 'Error al conectar con la base de datos'}), 500

        cursor = connection.cursor()

        cursor.execute("""
            SELECT nombres, apellidos, email, telefono, tipo, estado_suscripcion 
            FROM usuario WHERE email = %s
        """, (email,))
        user = cursor.fetchone()

        if user:
            connection.close()
            return jsonify({
                'nombres': user[0],
                'apellidos': user[1],
                'email': user[2],
                'telefono': user[3],
                'tipo': user[4],
                'estado_suscripcion': user[5]
            }), 200
        else:
            connection.close()
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)