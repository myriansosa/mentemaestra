
from django.shortcuts import render, redirect
from .forms import IngreseNumero, Registrar, Elegir
from juego.models import Jugada, Partida, Jugador
from .mastermind import evaluar, crear_numero
import random, string



def jugar(request, partida_id):
    jugadas = Jugada.objects.filter(partida__id=partida_id).order_by('-id')
    partida = Partida.objects.get(id=partida_id)
            
    if request.method == 'POST':
        form= IngreseNumero(request.POST)
        #validar=verificar(numero)
        if form.is_valid():
            jugador = partida.turno_de
            apuesta = form.cleaned_data["numero"]
            bien, regular = evaluar(apuesta, jugador.incognita)
            ronda = partida.ronda
            jugada = Jugada.objects.create(jugador=jugador, 
                partida=partida, apuesta=apuesta, bien=bien, 
                regular=regular, ronda=ronda)
            participantes = list(partida.participantes.all())
            print("turno de", partida.turno_de)
            try:
                partida.turno_de = participantes[participantes.index(jugador) + 1]
            except IndexError:
                partida.ronda = partida.ronda + 1
                partida.turno_de = participantes[0]
            
            partida.save()

            return redirect('jugar', partida_id=partida_id)
    else: 
        form= IngreseNumero()
    return render(request, 'comenzar.html', 
        {
        'jugadas':jugadas,
         'form': form,
         'partida': partida
        
        })

def inicio(request):
        partida = Partida.objects.create()
        if request.method == 'POST':
            form = Elegir(request.POST)
            if form.is_valid():
                privado = form.cleaned_data['privado']
                if privado == True:
                    partida.privado = privado
                    partida.codigo = ''.join(random.sample(string.ascii_letters, 8))
                    partida.save()
                    return redirect('registro/{}'.format(partida.codigo))
            else: 
                return redirect('registro/{}'.format(partida.id))
        else:
            form = Elegir()
            return render(request, 'inicio.html',
            {
             'form': form,
             })    


def registrar(request, id):
    #conprueba si es un mumero
    if id.isdigit():
        partida = Partida.objects.get(id=id)
    else:
        partida = Partida.objects.get(codigo=id)
    jugadores = partida.participantes.all()
    if request.method == 'POST':

        form= Registrar(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            incognita = crear_numero()
            jugador = Jugador.objects.create(nombre=nombre, 
                incognita=incognita, activo=True)
            if partida.participantes.count() == 0:
                # el primer turno es del primer registrado
                partida.turno_de = jugador
                partida.save() 
            partida.participantes.add(jugador)
            
            if 'comenzar' in request.POST:
                # apretaron el boton verde para comenzar el juego
                return redirect('jugar', partida_id=id)
            return redirect('/registro/{}'.format(partida.id))

    else: 
        form= Registrar()
    return render(request, 'registrar.html', 
        {
        'jugadores':jugadores,
         'form': form,
        })
    

