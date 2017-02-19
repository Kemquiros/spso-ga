
# coding: utf-8

#---------------------------------------------------------
#Importaciones
#---------------------------------------------------------

from __future__ import division #Float division
from collections import Counter
import matplotlib.pyplot as plt
from random import *

#---------------------------------------------------------
#---------------------------------------------------------
#Parámetros del problema
#---------------------------------------------------------
#---------------------------------------------------------

args ={'TimeSlot': 15, 'Groups': 12,'Profesores':24, 'MateriasMaximas':3, 'Materias':10}

#---------------------------------------------------------
#---------------------------------------------------------
#Parámetros del algoritmo
#---------------------------------------------------------
#---------------------------------------------------------

param = {'ParticulasxEnjambre': 8,'Enjambres': 10,'Iteraciones': 100,'c1':2.05,'c2':2.05,'k':0.72984, 'rondaAparemiento':5}
infinito = 9999999999999


#---------------------------------------------------------
#---------------------------------------------------------
#Definición de clases
#---------------------------------------------------------
#---------------------------------------------------------

class Particula:
    def __init__(self, vectorPosicion, vectorVelocidad):
        self.pos = vectorPosicion
        self.vel = vectorVelocidad
        self.f= infinito
        self.mejorPos = [] #Mejor posición personal conocida
        self.mejorF = infinito #Fitness correspondiente a la mejor posición personal conocida
        self.fAcumulado = 0
    
        
class Enjambre:
    
    def __init__(self):
        self.particulas=[]
        self.mejorPos = [] #Mejor posición local conocida
        self.mejorF = infinito  #Fitness correspondiente a la mejor posición local conocida
        self.mejorParticula = -1
        self.disponible = 0
    def setParticula(self, x):
        self.particulas.append(x)
    def delParticula(self, indice):
        del self.particulas[indice]
    def getParticula(self, indice):
        return self.particulas[indice] 
    def mParticula(self): #Mejor partícula
        mejor = self.particulas[0]
        for p in self.particulas:
            if mejor.fAcumulado > p.fAcumulado:
                mejor = p
        return mejor
    def pParticula(self): #Peor partícula
        peor = self.particulas[0]
        for p in self.particulas:
            if peor.fAcumulado < p.fAcumulado:
                peor = p
        return peor    
    def limpiarRendimiento(self):
        for p in self.particulas:
            p.fAcumulado = 0
            

#---------------------------------------------------------
#---------------------------------------------------------
#Definición de función objetivo
#---------------------------------------------------------
#---------------------------------------------------------


#Función objetivo a minimizar
def fitness(x):
    return constrain(x)

#Función que según las entradas
#retorna la penalización
def constrain(x):
    return constrain1(x)+constrain2(x)+constrain3(x)

#Entre más aparaciones tiene un profesor para un grupo
#Más alta es la penalización
def constrain1(x):
    penalizacion=0
    for i in range(args['Groups']) :
        aux=[0]*args['TimeSlot']
        for j in range(args['TimeSlot']):
            #Toma como vector todos los slots de un grupo
            #print ('Indice: '+str(i+(j*args['Groups'])))
            aux[j]=x[i+(j*args['Groups'])]
        c=Counter(aux)
        for j in c:
            if c[j]>1:#Aparece más de una vez
                #Ya que si hay 3 elementos, sólo suma 2 que es el exceso
                penalizacion+=c[j]-1
    #print('Penalizacion #1 = '+str(penalizacion))        
    return penalizacion

#A menor cantidad de profesores asignados, mayor penalización
#retorna el inverso de la cantidad de profesores activos
#retorna profesoresExistentes/profesoresActivos
def constrain2(x):
    numProfesoresActivos=0
    profesoresActivos = [0]*args['Profesores']
    #print('profesores activos',profesoresActivos)
    c = Counter(x)
    #mensaje('---> c ',str(c))
    for codigo in c:
        #indice de profesores por materia
        if c[codigo]!=0:
            #print('codigo ',codigo)
            profesorActual=profesoresXmateria[codigo]['profesor']   
            #print('profesorActual',profesorActual)
        profesoresActivos[profesorActual-1]+=1
        #print('profesores activos',profesoresActivos)
        
    
    numProfesoresActivos= sum(profesoresActivos)
    #print('Profesores activos = '+str(numProfesoresActivos))
    #print('Profesores totales = '+str(args['profesores']))
    penalizacion=(args['Profesores']/numProfesoresActivos)-1
    #print('Penalizacion #2 = '+str(penalizacion))
    return penalizacion

#Penaliza la no uniformidad en la frecuencia de actividad de los profesores
#Calcula la moda de actividad, y penaliza la distancia de cada profesor a la moda
def constrain3(x):
    penalizacion = 0
    c = Counter(x)
    moda= c.most_common(1)
    moda = moda[0][1]
    for i in c:
        penalizacion+=abs(moda-c[i])
        #print(abs(moda-c[i]))
    #print('Penalizacion #3 = '+str(penalizacion))
    return penalizacion




#---------------------------------------------------------
#---------------------------------------------------------
#       Generación de las Materias por Profesor
#---------------------------------------------------------
#---------------------------------------------------------




#Partiendo del supuesto de que se cuenta con 16 profesores
#1 profesor por cada grupo (director de grupo) = 12 profesores
#1/3 de dichos profesores = 4 profesores
profesoresXmateria={1: {'profesor': 1, 'materia': 5}}
def generarMateriasProfesor():

    indiceAux = 0
    #Se le asigna un número de materias a cada profesor
    for i in range(0,args['Profesores']):
        #Genera un número aleatorio entre 1 y el número de materias maximas que puede tener un profesor
        numeroMaterias = randint(1,args['MateriasMaximas'])
        print('Profesor '+str(i+1)+' -> Materias '+str(numeroMaterias))
        #Se le asigna cuáles son dichas materias
        for j in range(0,numeroMaterias):
            indiceAux+=1
            #Genera una materia aleatoria
            materiaNueva =  randint(1,args['Materias'])
            #Se asigna el profesor-materia al diccionario
            profesoresXmateria[indiceAux] = {'profesor':i+1,'materia':materiaNueva}
            
    #Un código se define como profesor X con la materia Y
    args['codigos']=indiceAux 
    print profesoresXmateria



#---------------------------------------------------------
#---------------------------------------------------------
#            Disponibilidad de profesores
#---------------------------------------------------------
#---------------------------------------------------------

# Se crea la matriz de disponibilidad de profesores 
# Las filas son profesores, columnas cada TimeSlot
disponibilidad = [0] * args['Profesores']
def generarDisponibilidad():
    
    for i in range(0,args['Profesores']):
        disponibilidad[i] = [0] * args['TimeSlot']* args['Groups']

    # Se inicializa la matriz de disponibilidad aleatoriamente

    for fila in disponibilidad:
        for c in range(len(fila)):
            aux =randint(1,2)
            if  (aux == 1):
                fila[c]=1
    print disponibilidad


#---------------------------------------------------------
#---------------------------------------------------------
#            Generar particulas
#---------------------------------------------------------
#---------------------------------------------------------

def mensaje(m1,m2):
    print(m1+' -> '+str(m2))
    
def cambiarCodigoPorProfesor(lista):
    listaProfesor = [0]*len(lista)
    #print('lista-codigo'+str(lista))
    for i in range(0,len(lista)):
        #print('l-codigo '+str(lista[i]))
        listaProfesor[i]= extraeProfesor(lista[i])
        #print('l-profesor '+str(listaProfesor[i]))
    #print('lista-profesor'+str(listaProfesor))
    return listaProfesor

def extraeProfesor(codigo):
    if codigo == -1:
        return codigo
    else:
        return profesoresXmateria[codigo]['profesor']-1#Indices desde 0 hasta profesor-1

#Comprueba la disponibilibidad del profesor perteneciente a ese código en ese TimeSlot 
def comprobarCodigo(codigo,dimension):
    prof = extraeProfesor(codigo) #Extrae el profesor perteneciente a ese código 
    
    if disponibilidad[prof][dimension] == 1:#Comprueba la disponibilidad de ese profesor en ese TimeSlot
        return True
    else:
        return False
def comprobarBilocacion(lista,codigo,dimension) :
    #mensaje('>> Lista completa: ',lista)
    #dimension+=1 #0-15 pasa a 1-16
    #mensaje('dimensión a procesar: ',dimension)
    cuadrante = dimension//args['TimeSlot'] #División entera para conocer el cuadrante
    limiteInferior = cuadrante * args['TimeSlot'] #Extremo incluido
    #mensaje('limiteInf',limiteInferior)
    limiteSuperior = ((cuadrante + 1) * args['TimeSlot']) #Extremo sin incluir
    #mensaje('limiteSup',limiteSuperior)
    listaCodigo = lista[limiteInferior:limiteSuperior]
    #mensaje('>> Sublista: ',listaCodigo)
    listaProfesor = cambiarCodigoPorProfesor(listaCodigo)
    prof = extraeProfesor(codigo)
    #mensaje('Codigo a ingresar -> ',codigo)
    #mensaje('Profesor a ingresar -> ',prof)
    if prof not in listaProfesor: #Si el profesor no esta en la subLista, es decir no está dictando clase en ese TimeSlot
        #print ('>> No está')
        return True
    else:
        #print ('>> Está')
        return False
    

#---------------------------------------------------------
#---------------------------------------------------------
#              Genera las particulas iniciales
#---------------------------------------------------------
#---------------------------------------------------------

def generarParticulas(enjs):
    bla = 1
    for e in range(0,param['Enjambres']):#Por cada enjambre
        enjambre = Enjambre()        
        print ('***Enjambre***'+str(bla))
        #print enjambre
        for p in range(0,param['ParticulasxEnjambre']):#Por cada particula pertenenciente al enjambre
            print ('--------------->Particula Nueva '+ str(p+1))
            posicion=[-1]*args['TimeSlot']*args['Groups']#Se crea la posición de la particula con todas las dimensiones en cero
            velocidad=[-1]*args['TimeSlot']*args['Groups']#Se crea la velocidad de la particula con todas las dimensiones en cero
            for d in range(0,args['TimeSlot']*args['Groups']):#Por cada dimensión de la partícula     
            
                #----Generación de la posición----
                centinela1 = False#Controla que el profesor este disponible en ese TimeSlot
                centinela2 = False#Controla que el profesor no esté dictando en dos grupos a la vez
                cod = 0 #Inicializo la variable
                while centinela1 != True or centinela2 != True:#Mientras no este disponible el profesor perteneciente a ese código en ese TimeSlot
                    cod = randint(1,args['codigos'])#Genera un código aleatorio
                    centinela1 = comprobarCodigo(cod,d)
                    if centinela1 == True:
                        centinela2 = comprobarBilocacion(posicion,cod,d)
                posicion[d]=cod
                #-----------------------------------
            
                 #----Generación de la velocidad----
                velocidad[d]= randint(1,args['codigos'])
                #-----------------------------------
            
            part = Particula(posicion,velocidad)

            enjambre.setParticula(part)
        enjambres.append(enjambre)
        bla+=1
def imprimirParticula(p):
        print(' Posicion: '+str(p.pos))
        print(' Velocidad: '+str(p.vel))
    





def calcularFitness():
    cont = 1
    print('\n------------Ingresa a calcular Fitness\n')
    #mensaje('Cantidad de enjambres',len(enjambres))
    #mensaje('Enjmabre',str(enjambres))
    for e in enjambres:#Por cada enjambre
        for p in range(0,param['ParticulasxEnjambre']):#Por cada particula pertenenciente al enjambre
            particula = e.getParticula(p)
            particula.f=fitness(particula.pos)
            particula.fAcumulado += particula.f
            print('\nEmjambre '+str(cont)+'  Particula '+str(p+1))
            mensaje('Fitness',particula.f)
            imprimirParticula(particula)
            
            if particula.f < particula.mejorF: #Un fitness menor es mejor, porque posee menos penalización
                print('>>>>> Actualiza')
                print('Anterior f: '+str(particula.mejorF)+'  Actual: '+str(particula.f))
                print('Anterior pos: '+str(particula.mejorPos)+'  Actual: '+str(particula.pos))
                particula.mejorF = particula.f
                particula.mejorPos = particula.pos[:]      
        cont+=1
        
#Calcula el mejor de cada enjambre
def calcularEnjambre(rondaInicial):
        cont = 0
        print('\n-----------------Comienza calcular Enjambre -> rondaInicial: '+str(rondaInicial)+'\n')
        for e in enjambres:#Por cada enjambre
            actualiza = False
            if rondaInicial:                
                e.mejorF = e.particulas[0].f
                e.mejorPos = e.particulas[0].pos[:]                            
          
            #for p in range(inicial,param['ParticulasxEnjambre']):
            for p in e.particulas:
                print('Mejor enjambre:'+str(e.mejorF)+' > Particula:'+str(p.f))
                #print('Mejor indice: '+str(mejor)+'  Actual:'+str(p))
                if e.mejorF > p.f:
                    e.mejorF = p.f
                    e.mejorPos = p.pos[:]
                    print('>>>>>>>>> El enjambre actualiza. Anterior: '+str(e.mejorF)+' Actual: '+str(p.mejorF))                
            
            rendimiento[cont].append(e.mejorF)
            print('Rendimiento del enjambre #'+str(cont+1)+' -> '+str(rendimiento[cont]))
            print('Mejor particula del enjambre: '+str(e.mejorPos)+' rendimiento: '+str(e.mejorF)+'\n')
            cont+=1
        rondaInicial=False
        
def discretizarVelocidad(v):
    decimal = v%1 #Toma la parte decimal
    if decimal >= 0.5:
        return int(v)+1
    else:
        return int(v)
         

def anularAntiguosProfesores(listaProfesor,sublistaAuxiliar):
    l=listaProfesor[:]
    for i in range(0,len(listaProfesor)):
        if sublistaAuxiliar[i]==0:
            listaProfesor[i]=-1
    return l
    
#Actualiza posiciones y velocidades
#Si una particula posee bilocación muta la dimensión implicada
def actualizarEnjambre():                
    
    for e in enjambres:#Por cada enjambre
        mejorParticula = e.mejorPos
        for p in e.particulas:
            auxiliar = [0]*(args['TimeSlot']*args['Groups']) #Nos dice si ya se modificó la dimensión
            for d in range(0,args['TimeSlot']*args['Groups']):#Por cada dimensión de la partícula
                #print('>>  Dimesion '+str(d)+' <<')
                #Actualizar velocidades
                p.vel[d] = p.vel[d] + param['c1']*gauss(0.5,0.5)*(p.mejorPos[d]-p.pos[d]) + param['c2']*gauss(0.5,0.5)*(mejorParticula[d]-p.pos[d])
                p.vel[d] = p.vel[d]*param['k']                
                p.vel[d] = discretizarVelocidad(p.vel[d])
                #Actualizar posiciones
                p.pos[d] = ((p.pos[d] + p.vel[d]) % args['codigos']) +1 #Límite de hiperesfera
                centinela = False        
                
                cuadrante = d//args['TimeSlot'] #División entera para conocer el cuadrante
                limiteInferior = cuadrante * args['TimeSlot'] #Extremo incluido
                limiteSuperior = ((cuadrante + 1) * args['TimeSlot']) #Extremo sin incluir
                sublista = p.pos[limiteInferior:limiteSuperior]
                sublistaAuxiliar = auxiliar[limiteInferior:limiteSuperior]
                listaProfesor = cambiarCodigoPorProfesor(sublista)
                listafinal = anularAntiguosProfesores(listaProfesor,sublistaAuxiliar)
                prof = extraeProfesor(p.pos[d])

                while centinela == False:                    
                    if prof in listaProfesor:
                        
                        m=p.pos[d]
                        p.pos[d] = randint(1,args['codigos'])
                        print('__--MUTA--__ dimensión: '+str(d)+' viejo_código: '+str(m)+' nuevo_código: '+str(p.pos[d]))
                        prof = extraeProfesor(p.pos[d])
                    else:
                        centinela = True
                        auxiliar[d] = 1
                        
                                
                                

                
def mostrarParticulas():
    contador1=1
    for e in enjambres:#Por cada enjambre
        print('\n----------------- Enjambre #'+str(contador1))
        contador2=1
        for p in range(0,param['ParticulasxEnjambre']): 
            print('\n------- Particula #'+str(contador2))
            mensaje('Posicion',e.getParticula(p).pos)
            mensaje('Velocidad',e.getParticula(p).vel)
            contador2+=1
        contador1+=1
        print('\n')
             
def initRendimiento(r): 
    for i in range(param['Enjambres']):
        r.append([])
        



def cruzarEnjambre():
    #Limpia la dispnibilidad de los enjambres
    for e in enjambres:
        e.disponible = 0
    actual= 1   
    #Cruza
    for e in enjambres:
        #Si el ejambre actual está disponible
        if e.disponible == 0:
            e.disponible = 1 #Ya no está disponible
            
            centinela = False
            while centinela == False:  #Mientras no encuentre una pareja disponible              
                posiblePareja = randint(0,param['Enjambres']-1)
                #Si no es él mismo y el enjambre de apareo está disponible
                if enjambres[posiblePareja].disponible == 0:
                    centinela = True
                    enjambres[posiblePareja].disponible = 1 #Ya no está disponible
                    print('\n----------\nSe aparea enjambre #'+str(actual)+' y enjambre #'+str(posiblePareja+1)+'\n----------')
            #El enjambre actual encontro otro con el cual se puede aparear
            pareja = enjambres[posiblePareja]
            
            mejorParticula1 = e.mParticula() #Copia de la particula
            hijo1 = e.pParticula() #Trae a la peor particula
            
            mejorParticula2 = pareja.mParticula() #Copia de la particula
            hijo2 = pareja.pParticula() #Trae a la peor particula
            
            mensaje('Enjambre padre: Rendimiento mejor particula',mejorParticula1.fAcumulado)
            mensaje('Enjambre madre: Rendimiento mejor particula',mejorParticula2.fAcumulado)
            mensaje('Enjambre padre: Rendimiento peor particula',hijo1.fAcumulado)
            mensaje('Enjambre madre: Rendimiento peor particula',hijo2.fAcumulado)
            
            tam = len(mejorParticula1.pos)
            #Con esto se asegura que se cojan TimeSlots completos
            #Cumpliendo la restricción fuerte de bilocación
            mitad = (args['Groups']//2)*args['TimeSlot'] 
            
            hijo1.pos = ((mejorParticula1.pos[0:mitad])[:]) + ((mejorParticula2.pos[mitad:tam])[:])
            hijo2.pos = ((mejorParticula2.pos[0:mitad])[:]) + ((mejorParticula1.pos[mitad:tam])[:])
            
            
            mensaje('Padre',mejorParticula1.pos)
            mensaje('Madre',mejorParticula2.pos)
            mensaje('Hijo1',hijo1.pos)
            mensaje('Hijo2',hijo2.pos)
            
            hijo1.vel = ((mejorParticula1.vel[0:mitad])[:]) + ((mejorParticula2.vel[mitad:tam])[:])
            hijo2.vel = ((mejorParticula2.vel[0:mitad])[:]) + ((mejorParticula1.vel[mitad:tam])[:])
                        
            hijo1.f= infinito
            hijo1.mejorPos = [] #No conoce mejor posición
            hijo1.mejorF = infinito #No conoce mejor fitness
            
            hijo2.f= infinito
            hijo2.mejorPos = [] #No conoce mejor posición
            hijo2.mejorF = infinito #No conoce mejor fitness
            
            e.limpiarRendimiento()
            pareja.limpiarRendimiento()
        actual+=1
 
#---------------------------------------------------------
#---------------------------------------------------------
#              Funciones para imprimir resultados
#---------------------------------------------------------
#---------------------------------------------------------           
            
def imprimirRendimiento(r):
    print('\n\n------------------------------------Rendimiento ----------------\n') 
	print(str(r))
    contador = 0
    for i in r:
        plt.plot(i)
        plt.ylabel('Rendimiento')  
        plt.xlabel('Iteraciones')
        contador +=1
    plt.show()
    
def imprimirResultado():
    print('\n\n------------------------------------Resultado ----------------\n')
    contador=1
    for e in enjambres:#Por cada enjambre
        print('\nEnjambre #'+str(contador)+'\nRendimiento:'+str(e.mejorF)+'\n Mejor particula:'+str(e.mejorPos))
        contador+=1


#---------------------------------------------------------
#---------------------------------------------------------
#              Inicializar Algoritmo
#---------------------------------------------------------
#---------------------------------------------------------

enjambres = []
rondaInicial = True
rendimiento = []

initRendimiento(rendimiento)    
generarMateriasProfesor()
generarDisponibilidad()
generarParticulas(enjambres)    


#---------------------------------------------------------
#---------------------------------------------------------
#              Iteración
#---------------------------------------------------------
#---------------------------------------------------------
    
for iteracion in range(1,param['Iteraciones']+1):
    print('\n')
    mensaje('------------------------------------RONDA ',str(iteracion+1))
    print('\n')
    calcularFitness() #Se calculca el fitness personal de la particula
    calcularEnjambre(rondaInicial) #Se reemplazan mejor fitness personal y local
    
    rondaInicial=False
    if iteracion != param['Iteraciones'] -1:
        actualizarEnjambre() #Se actualizan velocidades y posiciones
        if iteracion % param['rondaAparemiento'] == 0: #Cruza enjambres al azar
            cruzarEnjambre()
    
    #mostrarParticulas()

#---------------------------------------------------------
#---------------------------------------------------------
#              Resultado
#---------------------------------------------------------
#---------------------------------------------------------
imprimirRendimiento(rendimiento)
imprimirResultado()

   






