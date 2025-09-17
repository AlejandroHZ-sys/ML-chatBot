# -*- coding: utf-8 -*-
import re
import time
import sys
from datetime import datetime

# Nuevas subcategorías de sucursal
sucursal_ubicacion_RE = r"(sucursal(es)?|oficina(s)?|tienda(s)?|centro(s)?( de servicio)?|branch|store|ubicaci[oó]n|direcci[oó]n|domicilio|mapa|localizar|d[oó]nde|queda|cercan[ao]s?)"
sucursal_horario_RE   = r"(horario(s)?|hora(s)?|abre(n)?|cierran?|apertura|cierre|atenci[oó]n)"
sucursal_servicios_RE = r"(servicio(s)?|disponible(s)?|ofrecen|puedo hacer|hay en la sucursal|tr[aá]mites)"
sucursal_apertura_RE  = r"(apertura|cierre|abrir|cerrar|a qu[eé] hora)"
sucursal_acciones_RE  = r"(pagar|recoger|enviar|tramite|permiten|que se puede|hacer en la sucursal)"
sucursal_estacionamiento_RE = r"(estacionamiento|parqueo|caj[oó]n|d[oó]nde (puedo|se puede) estacionar)"
sucursal_accesibilidad_RE = r"(accesible|silla de ruedas|discapacitados|rampa|acceso)"
sucursal_pago_RE = r"(pago|efectivo|tarjeta|aceptan|formas de pago)"

# Regex con más variaciones y frases coloquiales
ubicacion_paquete_RE = r"(d[oó]nde (est[áa]|anda|va) (mi|el)?.*paquete)"
ubicacion_sucursal_RE = r"(d[oó]nde (est[áa]|queda|hay)?.*sucursal)"
tracking_RE   = r"(rastreo|tracking|seguimiento|localiza(r|ci[oó]n)|dónde (está|anda|va) mi paquete|ubicaci[oó]n.*paquete|mi paquete|seguir.*paquete|cuando.*entregan.*paquete|paq(u|ue)te)"
pickup_RE     = r"(recogida|pickup|agendar (recogida|env[ií]o)|programar (env[ií]o|paquete)|quiero que lo recojan|pasen por mi paquete)"
tarifa_RE     = r"(cotiza(r|ci[óo]n)|precio|tarifa|costo|cu[áa]nto vale|cu[áa]nto cuesta|cu[áa]nto sale|quiero saber.*(cuesta|precio)|promociones|costos)"
sucursal_RE = (sucursal_ubicacion_RE + "|" +sucursal_horario_RE   + "|" +sucursal_servicios_RE + "|" +sucursal_apertura_RE  + "|" +sucursal_acciones_RE + "|" + sucursal_estacionamiento_RE + "|" + sucursal_accesibilidad_RE + "|" + sucursal_pago_RE)
aduana_RE     = r"(aduana|aduna|impuesto|tax|documentaci[oó]n|pago pendiente|retenci[oó]n|servicio de aduana)"
fallida_RE    = r"(entrega fallida|no lleg[óo]|no entregado|no lo recib[ií]|no recibi|no lleg[óo] mi paquete|no tengo mi paquete|porque no.*(recib|tengo|llego).*paquete|reprogramar|devoluci[óo]n|reclamo|incidente|por qu[ée] no)"
crear_RE      = r"(crear env[íi]o|nuevo env[íi]o|enviar paquete|quiero enviar|generar gu[íi]a|mandar un paquete|hacer un env[íi]o|como (hago|crear|realizo) un env[íi]o)"
agente_RE     = r"(hablar con humano|agente|soporte real|asesor|supervisor|empleado real|persona real|pasame (un|a) (humano|gerente|persona)|necesito (hablar|ayuda) con (alguien|una persona)|quiero hablar con un asistente)"
salir_RE      = r"(salir|adi[oó]s|terminar|gracias|ya no|bye|nos vemos|no|nada)"
exit_RE = re.compile(r"^(salir|adios|adiós|terminar|gracias|quit|exit|q)$", re.I)

aduana_pagar_RE = re.compile(r"(pagar|pago|comprobante|liquidar|link|enlace|1|uno|primero)", re.I)
aduana_docs_RE = re.compile(r"(documentos|subir|enviar|adjuntar|adjunto|mandar documentos|subida|2|dos|segundo)", re.I)
aduana_info_RE = re.compile(r"(informaci[oó]n|info|detalles|explicaci[oó]n|saber m[aá]s|3|tres|por qu[eé]|motivo|raz[oó]n)", re.I)
aduana_agent_RE = re.compile(r"(agente|aduanal|contactar|llamar|especialista|asesor|humano|persona|representante|4|cuatro)", re.I)
aduana_detalles_RE = re.compile(r"(detalles|ver|estado|status|seguimiento|tracking|d[oó]nde|ubicaci[oó]n|1|uno|primero)", re.I)
# Intenciones operativas — se preguntará si el usuario necesita más ayuda
aduana_programar_RE = re.compile(r"(programar|agendar|entrega|fecha|hora|cita|recogida|pickup|2|dos|cuando|cu[aá]ndo)", re.I)
aduana_recoger_RE = re.compile(r"(recoger|sucursal|oficina|centro|buscar|pasar por|ir por|retirar|3|tres|tercero)", re.I)
# 'volver al menu' y 'salir' detectables aquí
aduana_menu_RE = re.compile(r"(volver al menu|menu|volver al menú|volver|regresar|principal|atr[aá]s|finalizar|terminar|4|5|cuatro|cinco|no|n)", re.I)
aduana_exit_RE = re.compile(r"(salir|adios|adiós|terminar|finalizar|quit|exit|q|5|6)", re.I)



# Dataset ficticio de sucursales por ciudad
sucursales = {
    "cdmx": {
        "alias": [r"\b(cdmx|ciudad de méxico|df|distrito federal|capital|méxico)\b"],
        "direccion": "Av. Paseo de la Reforma 123, Col. Juárez, CDMX",
        "horario": "Lunes a viernes 9:00 - 18:00, sábados 9:00 - 14:00",
        "servicios": "Envío y recolección de paquetes, pago de servicios, asesoría personalizada",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "monterrey": {
        "alias": [r"\b(monterrey|mty|nuevo le[oó]n|mtrey)\b"],
        "direccion": "Av. Constitución 456, Col. Centro, Monterrey, NL",
        "horario": "Lunes a viernes 8:30 - 17:30, sábados 9:00 - 13:00",
        "servicios": "Envío de paquetes, recolección y atención empresarial",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": False,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "guadalajara": {
        "alias": [r"\b(guadalajara|gdl|jal|jalisco|ciudad de guadalajara)\b"],
        "direccion": "Av. Vallarta 789, Col. Americana, Guadalajara, JAL",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos nacionales e internacionales, recolección y pagos",
        "adicional": {
            "estacionamiento": False,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "puebla": {
        "alias": [r"\b(puebla|pue|angelopolis)\b"],
        "direccion": "Blvd. Héroes 321, Col. Centro, Puebla, PUE",
        "horario": "Lunes a viernes 9:00 - 17:00",
        "servicios": "Atención general, envíos nacionales, pagos",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo"
        }
    },
    "tijuana": {
        "alias": [r"\b(tijuana|bc|baja california|tj)\b"],
        "direccion": "Av. Revolución 123, Zona Centro, Tijuana, BC",
        "horario": "Lunes a viernes 8:00 - 18:00, sábados 9:00 - 13:00",
        "servicios": "Envíos nacionales e internacionales, atención personalizada",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "leon": {
        "alias": [r"\b(le[oó]n|gto|guanajuato)\b"],
        "direccion": "Blvd. Adolfo López Mateos 456, Col. Centro, León, GTO",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos, pagos y recolección de paquetes",
        "adicional": {
            "estacionamiento": False,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "queretaro": {
        "alias": [r"\b(querétaro|qro|queretaro capital)\b"],
        "direccion": "Av. Constituyentes 789, Col. Centro, Querétaro, QRO",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos nacionales, pagos y atención empresarial",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "cancun": {
        "alias": [r"\b(canc[uú]n|quintana roo|cancun)\b"],
        "direccion": "Av. Kukulcán 123, Zona Hotelera, Cancún, QROO",
        "horario": "Lunes a viernes 9:00 - 18:00, sábados 9:00 - 14:00",
        "servicios": "Envíos y recolección, pagos y asesoría",
        "adicional": {
            "estacionamiento": False,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "merida": {
        "alias": [r"\b(m[ée]rida|yucat[áa]n)\b"],
        "direccion": "Calle 60 456, Centro, Mérida, YUC",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos nacionales, pagos y recolección",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "toluca": {
        "alias": [r"\b(toluca|edomex|estado de m[eé]xico)\b"],
        "direccion": "Av. Lerdo 789, Col. Centro, Toluca, MEX",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos, pagos y atención general",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "ciudad juarez": {
        "alias": [r"\b(ciudad juárez|juárez|chihuahua|cd juárez)\b"],
        "direccion": "Av. Tecnológico 123, Ciudad Juárez, CHIH",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos nacionales, pagos y recolección",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "mexicali": {
        "alias": [r"\b(mexicali|bc|baja california)\b"],
        "direccion": "Av. Reforma 456, Mexicali, BC",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos nacionales e internacionales",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "saltillo": {
        "alias": [r"\b(saltillo|coahuila)\b"],
        "direccion": "Blvd. Nazario 789, Saltillo, COA",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos, pagos y recolección",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "veracruz": {
        "alias": [r"\b(veracruz|ver)\b"],
        "direccion": "Av. Independencia 123, Veracruz, VER",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos, pagos y atención general",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "acapulco": {
        "alias": [r"\b(acapulco|gro|guerrero)\b"],
        "direccion": "Costera Miguel Alemán 123, Acapulco, GRO",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos y recolección, pagos y asesoría",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "tampico": {
        "alias": [r"\b(tampico|tamps|tamaulipas)\b"],
        "direccion": "Av. Hidalgo 456, Tampico, TAMPS",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos nacionales, pagos y atención general",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "cuernavaca": {
        "alias": [r"\b(cuernavaca|mor|morelos)\b"],
        "direccion": "Av. Morelos 123, Cuernavaca, MOR",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos, pagos y recolección",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "chihuahua": {
        "alias": [r"\b(chihuahua|chih)\b"],
        "direccion": "Blvd. Universidad 456, Chihuahua, CHIH",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos, pagos y atención general",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    },
    "morelia": {
        "alias": [r"\b(morelia|mic|michoac[áa]n)\b"],
        "direccion": "Av. Madero 123, Morelia, MIC",
        "horario": "Lunes a viernes 9:00 - 18:00",
        "servicios": "Envíos nacionales, pagos y atención general",
        "adicional": {
            "estacionamiento": True,
            "accesibilidad": True,
            "metodos_pago": "Efectivo, Tarjeta de Crédito/Débito"
        }
    }
}


def detectar_ciudad(texto):
    for ciudad, data in sucursales.items():
        for patron in data["alias"]:
            if re.search(patron, texto, re.IGNORECASE):
                return ciudad
    return None

# Estado inicial
state = 0
Salida = True

print("Bienvenido al Chatbot de DHL. ¿En qué puedo ayudarte hoy?")
opcion = ""
while Salida:
    if state == 0:
        print("\nOpciones disponibles:")
        print("1. Rastreo de envíos")
        print("2. Agendar recogida")
        print("3. Cotización / tarifas")
        print("4. Localización de sucursales")
        print("5. Estado de aduanas")
        print("6. Entregas fallidas / reclamos")
        print("7. Crear un envío")
        print("8. Hablar con un agente humano")
        print("9. Salir")

        opcion = input("\nEscribe tu solicitud o número de opción: ").strip()

        # Si el usuario pone solo el número
        if opcion == "1":
            state = 1
        elif opcion == "2":
            state = 2
        elif opcion == "3":
            state = 3
        elif opcion == "4":
            state = 4
        elif opcion == "5":
            state = 5
        elif opcion == "6":
            state = 6
        elif opcion == "7":
            state = 7
        elif opcion == "8":
            state = 8
        elif opcion == "9":
            state = 9

        # Si escribe texto libre
        elif re.search(fallida_RE, opcion, flags=re.IGNORECASE):
            state = 6  # Prioridad sobre rastreo
        elif re.search(tracking_RE, opcion, flags=re.IGNORECASE):
            state = 1
        elif re.search(pickup_RE, opcion, flags=re.IGNORECASE):
            state = 2
        elif re.search(tarifa_RE, opcion, flags=re.IGNORECASE):
            state = 3
        elif re.search(sucursal_RE, opcion, flags=re.IGNORECASE):
            state = 4
        elif re.search(aduana_RE, opcion, flags=re.IGNORECASE):
            state = 5
        elif re.search(crear_RE, opcion, flags=re.IGNORECASE):
            state = 7
        elif re.search(agente_RE, opcion, flags=re.IGNORECASE):
            state = 8
        elif re.search(salir_RE, opcion, flags=re.IGNORECASE):
            state = 9
        else:
            print("Lo siento, no entendí tu solicitud. Intenta de nuevo.")
            state = 0

    # Opciones
    if state == 1:
        tracking = input("Ingresa tu número de guía: ")
        print(f"El envío con número {tracking} está en tránsito y llegará en 2 días hábiles.")
        state = 0

    if state == 2:
        print("Vamos a agendar una recogida de paquete.")

        # Pedir fecha
        fecha_str = input("Ingresa la fecha para la recogida (YYYY-MM-DD): ").strip()
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hoy = datetime.now().date()
            max_fecha = hoy.replace(day=hoy.day) + (datetime.now() - datetime.now())  # placeholder
            max_fecha = hoy.replace(day=hoy.day)  # ajustable si quieres límite
            # Validación básica
            if fecha < hoy:
                print("No puedes agendar una fecha pasada.")
                state = 0
                continue
            elif (fecha - hoy).days > 30:
                print("Solo es posible agendar dentro de los próximos 30 días.")
                state = 0
                continue
        except ValueError:
            print("Formato inválido de fecha. Usa YYYY-MM-DD (ej: 2025-09-20).")
            state = 0
            continue

        # Pedir hora
        hora_str = input("Ingresa la hora para la recogida (HH:MM en formato 24h, ejemplo 14:30): ").strip()
        try:
            hora = datetime.strptime(hora_str, "%H:%M").time()
            if hora.hour < 9 or hora.hour > 18:
                print("Nuestro horario de recolección es de 09:00 a 18:00.")
                state = 0
                continue
        except ValueError:
            print("Formato inválido de hora. Usa HH:MM (ej: 14:30).")
            state = 0
            continue

        print(f"Recogida programada para el {fecha} a las {hora_str}. Un mensajero irá a tu dirección registrada.")
        state = 0

    if state == 3:
        print("Cotización de envío")

        origen = input("Origen: ").lower()
        destino = input("Destino: ").lower()
        try:
            peso = float(input("Peso (kg): "))
        except ValueError:
            print("Por favor ingresa un número válido para el peso.")
            state = 0
            continue

        # Definición de zonas ficticias
        zonas = {
            "Norte": {
                "ciudades": ["tijuana", "mexicali", "ciudad juarez", "chihuahua", "saltillo", "monterrey"],
                "base": 150,
                "adicional": 50,
                "tiempo": "2-3 días hábiles"
            },
            "Centro": {
                "ciudades": ["cdmx", "queretaro", "toluca", "puebla", "leon", "morelia", "cuernavaca"],
                "base": 120,
                "adicional": 40,
                "tiempo": "1-2 días hábiles"
            },
            "Sur": {
                "ciudades": ["cancun", "merida", "acapulco", "veracruz", "tampico", "guadalajara"],
                "base": 140,
                "adicional": 45,
                "tiempo": "2-4 días hábiles"
            },
            "Internacional": {
                "ciudades": [],
                "base": 500,
                "adicional": 120,
                "tiempo": "5-7 días hábiles"
            }
        }

        # Detectar zona del destino
        zona_detectada = "Internacional"  # por defecto
        for zona, data in zonas.items():
            for ciudad in data["ciudades"]:
                if ciudad in destino.lower():
                    zona_detectada = zona
                    break

        # Obtener parámetros de la zona
        base = zonas[zona_detectada]["base"]
        adicional = zonas[zona_detectada]["adicional"]
        tiempo = zonas[zona_detectada]["tiempo"]

        # Calcular costo
        if peso <= 1:
            costo = base
        else:
            costo = base + (peso - 1) * adicional

        # Mostrar resultado
        print(f"\n📦 Envío {zona_detectada}:")
        print(f"De {origen} a {destino}")
        print(f"Peso: {peso} kg")
        print(f"💲 Costo estimado: ${costo:.2f} MXN")
        print(f"⏳ Tiempo estimado de entrega: {tiempo}")

        state = 0


    if state == 4:
        # Intenta detectar la ciudad en la primera pregunta del usuario
        ciudad = detectar_ciudad(opcion)
        contexto_sucursal = ciudad

        # Inicia el bucle de conversación para la sucursal
        while True:
            # Si no se detectó una ciudad en la pregunta inicial, pídele una al usuario
            if contexto_sucursal is None:
                ciudad_usuario = input("Claro, ¿en qué ciudad te gustaría buscar una sucursal? ").strip().lower()
                contexto_sucursal = detectar_ciudad(ciudad_usuario)

                if not contexto_sucursal:
                    print("Lo siento, no he encontrado sucursales en esa ciudad.")
                    state = 0  # Regresa al menú principal
                    break

            # Obtiene los datos de la sucursal del contexto
            data = sucursales[contexto_sucursal]

            # Revisa la intención del usuario en orden de especificidad (de más específica a más general)
            if re.search(sucursal_estacionamiento_RE, opcion, re.IGNORECASE):
                respuesta = "Sí, la sucursal cuenta con estacionamiento disponible." if data["adicional"][
                    "estacionamiento"] else "No, la sucursal no cuenta con estacionamiento propio, pero hay opciones cercanas."
                print(respuesta)
            elif re.search(sucursal_accesibilidad_RE, opcion, re.IGNORECASE):
                respuesta = "Sí, esta sucursal es accesible para personas con silla de ruedas." if data["adicional"][
                    "accesibilidad"] else "Lo siento, esta sucursal no cuenta con acceso para personas con movilidad reducida."
                print(respuesta)
            elif re.search(sucursal_pago_RE, opcion, re.IGNORECASE):
                print(
                    f"💳 En la sucursal de {contexto_sucursal.upper()} aceptamos: {data['adicional']['metodos_pago']}.")
            elif re.search(sucursal_servicios_RE, opcion, re.IGNORECASE) or re.search(sucursal_acciones_RE, opcion,
                                                                                      re.IGNORECASE):
                print(f"🔧 En la sucursal de {contexto_sucursal.upper()} puedes: {data['servicios']}.")
            elif re.search(sucursal_horario_RE, opcion, re.IGNORECASE):
                print(f"🕒 El horario de atención en {contexto_sucursal.upper()} es: {data['horario']}.")
            elif re.search(sucursal_ubicacion_RE, opcion, re.IGNORECASE):
                print(f"📍 La sucursal en {contexto_sucursal.upper()} está en: {data['direccion']}.")
            else:
                # Si no se detectó una intención específica, muestra toda la información
                print(f"Sucursal en {contexto_sucursal.upper()}:")
                print(f"📍 Dirección: {data['direccion']}")
                print(f"🕒 Horario: {data['horario']}")
                print(f"🔧 Servicios: {data['servicios']}")

            # Pregunta de seguimiento
            opcion = input(
                "\n¿Hay algo más que te gustaría saber sobre esta sucursal?").strip()

            # Salida del bucle
            if re.search(salir_RE, opcion, re.IGNORECASE):
                print("¡Claro! ¿Hay algo más en lo que pueda ayudarte?")
                state = 0
                break
    if state == 5:
        print("Tu envío está retenido en aduanas. Se requiere el pago de impuestos y documentación adicional.")
        state = 0

    if state == 6:
        print("Detectamos un intento de entrega fallido. Puedes reprogramar ingresando a tu portal DHL o llamando al 01-800-DHL.")
        state = 0

    if state == 7:
        destino = input("Destino del paquete: ")
        peso = input("Peso (kg): ")
        print(f"Guía generada para envío a {destino}, peso {peso} kg. Código: DHL{datetime.now().strftime('%H%M%S')}")
        state = 0

    if state == 8:
        print("Te conectamos con un agente humano... por favor espera.")
        Salida = False

    if state == 9:
        print("Gracias por usar el Chatbot DHL. Hasta pronto.")
        Salida = False
