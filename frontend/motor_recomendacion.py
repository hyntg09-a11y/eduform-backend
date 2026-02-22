def generar_recomendacion(respuestas):
    puntajes = {
        "Salud": 0,
        "Tecnologia": 0,
        "Educacion": 0,
        "Arte": 0,
        "Negocios": 0
    }

    # ===== Reglas vocacionales =====
    if respuestas.get("area_interes") == "Salud":       puntajes["Salud"] += 3
    if respuestas.get("area_interes") == "Tecnología":  puntajes["Tecnologia"] += 3
    if respuestas.get("area_interes") == "Educación":   puntajes["Educacion"] += 3
    if respuestas.get("area_interes") == "Arte":        puntajes["Arte"] += 3
    if respuestas.get("area_interes") == "Negocios":    puntajes["Negocios"] += 3

    if respuestas.get("estilo") == "Creativa":  puntajes["Arte"] += 2
    if respuestas.get("estilo") == "Analítica": puntajes["Tecnologia"] += 2
    if respuestas.get("estilo") == "Social":    puntajes["Educacion"] += 2
    if respuestas.get("estilo") == "Práctica":  puntajes["Salud"] += 2

    if respuestas.get("actividad") == "Resolver problemas": puntajes["Tecnologia"] += 2
    if respuestas.get("actividad") == "Ayudar personas":    puntajes["Salud"] += 2
    if respuestas.get("actividad") == "Crear cosas":        puntajes["Arte"] += 2
    if respuestas.get("actividad") == "Analizar datos":     puntajes["Negocios"] += 2

    if respuestas.get("trabajo") == "En equipo":  puntajes["Educacion"] += 1
    if respuestas.get("trabajo") == "Individual": puntajes["Tecnologia"] += 1
    if respuestas.get("trabajo") == "Mixto":      puntajes["Negocios"] += 1

    # ===== Perfil ganador =====
    perfil = max(puntajes, key=puntajes.get)

    # ===== Recomendaciones =====
    recomendaciones = {
        "Salud":      "Carreras en el área de la salud: Enfermería, Medicina, Psicología, Fisioterapia.",
        "Tecnologia": "Carreras tecnológicas: Ingeniería de Sistemas, Desarrollo de Software, Ciberseguridad.",
        "Educacion":  "Carreras educativas: Licenciaturas, Pedagogía, Psicología educativa.",
        "Arte":       "Carreras creativas: Diseño gráfico, Artes visuales, Producción audiovisual.",
        "Negocios":   "Carreras empresariales: Administración, Contaduría, Economía, Marketing."
    }

    return {
        "perfil": perfil,
        "recomendacion": recomendaciones[perfil]
    }
