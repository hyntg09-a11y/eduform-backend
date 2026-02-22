from evaluaciones.models import Carrera
perfiles = ['Salud', 'Tecnologia', 'Educacion', 'Arte', 'Negocios']
for p in perfiles:
    Carrera.objects.get_or_create(nombrecarrera=p, defaults={'nivelacademico': 'Universitario', 'duracionvalor': 4, 'duracionunidad': 'anos'})
print(Carrera.objects.count())