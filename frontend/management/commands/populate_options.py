from django.core.management.base import BaseCommand
from django.db import transaction
from evaluaciones.models import Pregunta, OpcionRespuesta

class Command(BaseCommand):
    """
    Comando de Django para poblar la base de datos con opciones de respuesta estándar.
    Crea las opciones "Sí" y "No" para cada pregunta existente que no las tenga.
    Es seguro ejecutarlo múltiples veces gracias a `get_or_create`.
    
    Uso: python manage.py populate_options
    """
    help = 'Crea opciones de respuesta estándar (Sí, No) para todas las preguntas existentes.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Iniciando el script para poblar opciones de respuesta..."))

        opciones_estandar = ["Sí", "No"]
        todas_las_preguntas = Pregunta.objects.all()
        
        if not todas_las_preguntas.exists():
            self.stdout.write(self.style.WARNING("No se encontraron preguntas en la base de datos. Abortando."))
            return

        opciones_creadas_count = 0

        for pregunta in todas_las_preguntas:
            for texto_opcion in opciones_estandar:
                _, created = OpcionRespuesta.objects.get_or_create(
                    idpregunta=pregunta,
                    texto=texto_opcion
                )
                if created:
                    opciones_creadas_count += 1

        self.stdout.write(self.style.SUCCESS(f"¡Proceso completado!"))
        self.stdout.write(f"Se crearon {opciones_creadas_count} nuevas opciones de respuesta.")
        self.stdout.write(f"Total de opciones en la BD: {OpcionRespuesta.objects.count()}")