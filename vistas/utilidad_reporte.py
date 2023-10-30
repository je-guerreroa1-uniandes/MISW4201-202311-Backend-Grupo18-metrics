from sqlalchemy.exc import IntegrityError

from modelos import \
    db, \
    Ejercicio, \
    Entrenamiento, Rutina


class UtilidadReporte:
    def print_something():
        return "something"

    def calcular_imc(self, talla, peso):
        return peso / (talla*talla)
        
    def dar_clasificacion_imc(self, imc):
        if imc<18.5:
            return "Bajo peso"
        elif imc<25:
            return "Peso saludable"
        elif imc<30:
            return "Sobrepeso"
        else:
            return "Obesidad"
            
    def dar_resultados(self, entrenamientos, entrenamientos_rutina):
        calorias_ejercicio = {}
        repeticiones_ejercicio = {}
        calorias_rutina = {}
        repeticiones_rutina = {}
        resultados = []
        
        calorias_total = 0
        repeticiones_total = 0

        # Entrenamientos por ejercicios
        for entrenamiento in entrenamientos:
            repeticiones_temp = entrenamiento.repeticiones
            calorias_temp = self.calcular_calorias(entrenamiento)

            # Acumular repeticiones por fecha
            if str(entrenamiento.fecha) in repeticiones_ejercicio:
                repeticiones_ejercicio[str(entrenamiento.fecha)] = repeticiones_ejercicio[str(entrenamiento.fecha)] + repeticiones_temp
            else:
                repeticiones_ejercicio[str(entrenamiento.fecha)] = repeticiones_temp

            # Acumular calorias por fecha
            if str(entrenamiento.fecha) in calorias_ejercicio:
                calorias_ejercicio[str(entrenamiento.fecha)] = calorias_ejercicio[str(entrenamiento.fecha)] + calorias_temp
            else:
                calorias_ejercicio[str(entrenamiento.fecha)] = calorias_temp

            calorias_total = calorias_total + calorias_temp
            repeticiones_total = repeticiones_total + repeticiones_temp

        # Creacion de filas de resultados
        for fecha_resultados in list(repeticiones_ejercicio.keys()):
            fila = dict(fecha=fecha_resultados, repeticiones=str(repeticiones_ejercicio[str(fecha_resultados)]), is_rutina='false', calorias=str(calorias_ejercicio[str(fecha_resultados)]))
            resultados.append(fila)

        # Entrenamientos por ejercicios
        for entrenamiento_rutina in entrenamientos_rutina:
            repeticiones_temp = entrenamiento_rutina.repeticiones
            calorias_temp = self.calcular_calorias_rutina(entrenamiento_rutina)

            rutina = Rutina.query.get_or_404(entrenamiento_rutina.rutina)
            repeticiones_temp = (entrenamiento_rutina.repeticiones * len(rutina.ejercicios))
            # Acumular repeticiones por fecha
            if str(entrenamiento_rutina.fecha) in repeticiones_rutina:
                repeticiones_rutina[str(entrenamiento_rutina.fecha)] = repeticiones_rutina[
                                                                       str(entrenamiento_rutina.fecha)] + repeticiones_temp
            else:
                repeticiones_rutina[str(entrenamiento_rutina.fecha)] = repeticiones_temp

            # Acumular calorias por fecha
            if str(entrenamiento.fecha) in calorias_rutina:
                calorias_rutina[str(entrenamiento_rutina.fecha)] = calorias_rutina[
                                                                       str(entrenamiento_rutina.fecha)] + calorias_temp
            else:
                calorias_rutina[str(entrenamiento_rutina.fecha)] = calorias_temp

            calorias_total = calorias_total + calorias_temp
            repeticiones_total = repeticiones_total + repeticiones_temp

        # Creacion de filas de resultados
        for fecha_resultados in list(repeticiones_rutina.keys()):
            fila = dict(fecha=fecha_resultados, repeticiones=str(repeticiones_rutina[str(fecha_resultados)]),
                            is_rutina='true', calorias=str(calorias_rutina[str(fecha_resultados)]))
            resultados.append(fila)

        # Totales
        resultados.append(dict(fecha='Total', repeticiones=str(repeticiones_total), calorias=str(calorias_total)))
        return resultados
        
    def calcular_calorias(self, entrenamiento):
        ejercicio = Ejercicio.query.get_or_404(entrenamiento.ejercicio)
        tiempo_segundos = (entrenamiento.tiempo.hour*60*60) + (entrenamiento.tiempo.minute*60) + entrenamiento.tiempo.second
        return ((4*entrenamiento.repeticiones*entrenamiento.repeticiones*ejercicio.calorias)/tiempo_segundos)

    def calcular_calorias_rutina(self, entrenamiento_rutina):
        rutina = Rutina.query.get_or_404(entrenamiento_rutina.rutina)
        conteo_calorico = 0.0
        for ejercicio in rutina.ejercicios:
            tiempo_segundos = entrenamiento_rutina.tiempo_segundos()
            conteo_calorico += self.calorias_por_ejercicio(ejercicio, entrenamiento_rutina.repeticiones,
                                                               tiempo_segundos)
        return conteo_calorico

    def calorias_por_ejercicio(self, ejercicio: Ejercicio, repeticiones: float, tiempo_segundos):
        return ((4 * repeticiones * repeticiones * ejercicio.calorias) / tiempo_segundos)
 