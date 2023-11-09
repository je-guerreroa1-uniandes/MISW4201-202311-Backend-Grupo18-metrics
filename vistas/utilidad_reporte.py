from sqlalchemy.exc import IntegrityError

from modelos import \
    db, \
    Ejercicio, \
    Entrenamiento, Rutina
from collections import defaultdict


class UtilidadReporte:
    def accumulate_stats(self, fecha, repeticiones_temp, calorias_temp, repeticiones_dict, calorias_dict):
        repeticiones_dict[fecha] += repeticiones_temp
        calorias_dict[fecha] += calorias_temp

    def create_results_row(self, fecha, repeticiones, calorias, is_rutina):
        return {'fecha': fecha, 'repeticiones': str(repeticiones), 'is_rutina': str(is_rutina).lower(), 'calorias': str(calorias)}

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
        # Using defaultdict to simplify accumulation logic
        repeticiones_ejercicio = defaultdict(int)
        calorias_ejercicio = defaultdict(int)
        repeticiones_rutina = defaultdict(int)
        calorias_rutina = defaultdict(int)
        resultados = []

        calorias_total = 0
        repeticiones_total = 0

        # Process entrenamientos
        for entrenamiento in entrenamientos:
            fecha = str(entrenamiento.fecha)
            repeticiones_temp = entrenamiento.repeticiones
            calorias_temp = self.calcular_calorias(entrenamiento)
            self.accumulate_stats(fecha, repeticiones_temp, calorias_temp, repeticiones_ejercicio, calorias_ejercicio)
            calorias_total += calorias_temp
            repeticiones_total += repeticiones_temp

        # Process entrenamientos_rutina
        for entrenamiento_rutina in entrenamientos_rutina:
            fecha = str(entrenamiento_rutina.fecha)
            calorias_temp = self.calcular_calorias_rutina(entrenamiento_rutina)
            rutina = Rutina.query.get_or_404(entrenamiento_rutina.rutina)
            repeticiones_temp = (entrenamiento_rutina.repeticiones * len(rutina.ejercicios))
            self.accumulate_stats(fecha, repeticiones_temp, calorias_temp, repeticiones_rutina, calorias_rutina)
            calorias_total += calorias_temp
            repeticiones_total += repeticiones_temp

        # Create results for ejercicios
        for fecha, repeticiones in repeticiones_ejercicio.items():
            resultados.append(self.create_results_row(fecha, repeticiones, calorias_ejercicio[fecha], False))

        # Create results for rutinas
        for fecha, repeticiones in repeticiones_rutina.items():
            resultados.append(self.create_results_row(fecha, repeticiones, calorias_rutina[fecha], True))

        # Totals
        resultados.append(self.create_results_row('Total', repeticiones_total, calorias_total, 'Total'))

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
 