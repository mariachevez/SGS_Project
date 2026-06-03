def validar_cedula(cedula):
    if len(cedula) != 10:
            raise Exception("Cédula con longitud incorrecta")
        
    if not cedula.isdigit():
        raise Exception("Por favor ingrese solo números")
    
    provincia = int(cedula[:2])
    if provincia < 1 or provincia > 24:
        raise Exception("El código de provincia no es válido (01–24).")
    
    tercer_digito = int(cedula[2])
    
    if tercer_digito >= 6:
        raise Exception("El tercer dígito no corresponde a una cédula de persona natural.")
    
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i, coef in enumerate(coeficientes):
        producto = int(cedula[i]) * coef
        if producto >= 10:
            producto -= 9
        total += producto

    digito_verificador = int(cedula[9])
    resultado = (10 - (total % 10)) % 10

    if resultado != digito_verificador:
        raise Exception("La cédula ingresada no es válida.")

    return cedula