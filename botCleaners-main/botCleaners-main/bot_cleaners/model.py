from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

import random
import itertools as it
import math
import numpy as np


class Celda(Agent):
    def __init__(self, unique_id, model, suciedad: bool = False, valor = 0):
        super().__init__(unique_id, model)
        self.sucia = suciedad
        self.value = valor


class Mueble(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class EstacionCarga(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
    


class RobotLimpieza(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100
        self.charging = False
        self.list = []
        self.list2 = []
        self.cuadrante = 0
        self.model = model
        self.clean = False
        self.can_carg = 0
        
    def limpiar_una_celda(self, celda_a_limpiar):
        x, y = self.pos
        diferencia_x = abs(self.pos[0] - celda_a_limpiar.pos[0])
        diferencia_y = abs(self.pos[1] - celda_a_limpiar.pos[1])

        if diferencia_x > 1 or diferencia_y > 1:
            self.mover_hacia_celda(celda_a_limpiar)

        if diferencia_x <= 1 and diferencia_y <= 1:
            celda_a_limpiar.sucia = False
            self.carga -= 2
            self.sig_pos = celda_a_limpiar.pos

    
    def mover_hacia_celda(self, celda):
        x, y = self.pos
        if (self.pos[0] - celda.pos[0] == 2):
            x -= 1
        if (self.pos[0] - celda.pos[0] == -2):
            x += 1
        if (self.pos[1] - celda.pos[1] == 2):
            y -= 1
        if (self.pos[1] - celda.pos[1] == -2):
            y += 1

        self.sig_pos = x, y


    def seleccionar_nueva_pos(self, lista_de_vecinos):
        self.sig_pos = self.random.choice(lista_de_vecinos).pos

    @staticmethod
    def buscar_celdas_sucia(lista_de_vecinos):
        # #Opción 1
        return [vecino for vecino in lista_de_vecinos
                         if isinstance(vecino, Celda) and vecino.sucia]
        # #Opción 2
        """
        celdas_sucias = list()
        for vecino in lista_de_vecinos:
            if isinstance(vecino, Celda) and vecino.sucia:
                celdas_sucias.append(vecino)
        return celdas_sucias
        """
    
    
    def buscar_carga(self):

        x, y = self.pos

        posCarga = {
            "1": (0,10),
            "2": (10,19),
            "3": (9,0),
            "4": (19,9)
        }

        final_pos = posCarga[str(self.cuadrante)]

        contents = self.model.grid.get_cell_list_contents([self.pos])
        if any(isinstance(obj, Celda) and obj.sucia for obj in contents):
            celda_actual = next(obj for obj in contents if isinstance(obj, Celda) and obj.sucia)
            self.limpiar_una_celda(celda_actual)

        vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)
        
        vecinos_sm = [x for x in vecinos if not isinstance(x, Mueble)]

        if x != final_pos[0]:
            if x > final_pos[0]:
                x -= 1
            else:
                x += 1
        
        if y != final_pos[1]:
            if y > final_pos[1]:
                y -= 1
            else:
                y += 1

        next_pos = x, y
        self.list2.append(self.pos)
        
        next_mueble = self.model.grid.get_cell_list_contents([next_pos])
        if any(isinstance(obj, Mueble) for obj in next_mueble):
            self.seleccionar_nueva_pos(vecinos_sm)
        
        else:
            self.sig_pos = x,y

    
        if (self.pos == final_pos and self.clean == False):
            self.charging = True
            self.carga += 5
        
        if (self.pos == final_pos and self.carga >= 85 and self.clean == False):
            self.charging = False
            self.can_carg = self.can_carg + 1
        
        if (self == final_pos and self.carga < 100 and self.clean == True):
            self.carga += 2

    def carga_final(self):
        x, y = self.pos

        posCarga = {
            "1": (0, 10),
            "2": (10, 19),
            "3": (9, 0),
            "4": (19, 9)
        }

        final_pos = posCarga[str(self.cuadrante)]

        vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)
        
        vecinos_sm = [x for x in vecinos if not isinstance(x, Mueble) and x.pos not in self.list2]


        if self.pos != final_pos:
            if x != final_pos[0]:
                if x > final_pos[0]:
                    x -= 1
                else:
                    x += 1

            if y != final_pos[1]:
                if y > final_pos[1]:
                    y -= 1
                else:
                    y += 1

        next_pos = x, y
        self.list2.append(self.pos)

        next_mueble = self.model.grid.get_cell_list_contents([next_pos])
        if any(isinstance(obj, Mueble) for obj in next_mueble):
            self.seleccionar_nueva_pos(vecinos_sm)
        else:
            self.sig_pos = next_pos

        if self.pos == final_pos and self.carga < 100:
            self.carga += 2

        if self.pos == final_pos and self.carga == 100:
            self.clean = True



    def step(self):
        esta_sucio = get_sucias(self.model)
        if esta_sucio == 0:
            self.clean == True
            self.carga_final()
            print(self.can_carg)

        else:
            #print("Sucio")
            cuadrantes = {
                "1": list(it.product(range(0,10), range(10,20))),
                "2": list(it.product(range(10,20), range(10,20))),
                "3": list(it.product(range(0,10), range(0,10))),
                "4": list(it.product(range(10,20), range(0,10)))
            }

            # Vecinos original
            vecinos = self.model.grid.get_neighbors(
                self.pos, moore=True, include_center=False)
            
            # Vecinos Original sin muebles
            vecinos_o_sm = [x for x in vecinos if not isinstance(x, Mueble)] 
            vecinos_o_v = [] #Vecinos Original que no ha visitado
            vecinos_o_c = [] #Vecinos Original que estan el cuadrante

            for x in vecinos_o_sm:
                if x.pos not in self.list:
                    vecinos_o_v.append(x)

            for x in vecinos_o_v:
                if x.pos in cuadrantes[str(self.cuadrante)]:
                    vecinos_o_c.append(x)

            vecinos_e = []
            vecinos_e_v = [] #Vecinos Extendidos que no ha visitado
            vecinos_e_c = [] #Vecinos Extendidos que estan el cuadrante

            for x in vecinos:
                vecinos_e.extend(
                    self.model.grid.get_neighbors(
                        x.pos, moore=True, include_center=False
                    )
                )
            
            # Vecinos Extendidos sin muebles
            vecinos_e_sm = [x for x in vecinos_e if not isinstance(x, Mueble)]

            for x in vecinos_e_sm:
                if x.pos not in self.list:
                    vecinos_e_v.append(x)
            
            for x in vecinos_e_v:
                if x.pos in cuadrantes[str(self.cuadrante)]:
                    vecinos_e_c.append(x)

            """vecinos2 = [] # Vecinos extendidos
            vecinos4 = [] # Los que no ha visitado
            vecinos5 = [] # Que esten en el cuadrante

            if (len(vecinos_o_c) == 0 and (len(vecinos_e_c) == 0)):
                for x in vecinos_o_sm:
                    if x.pos in cuadrantes[str(self.cuadrante)]:
                        vecinos_o_c.append(x)"""
            if len(vecinos_e_c) == 0:
                for x in vecinos_e_sm:
                    if x.pos in cuadrantes[str(self.cuadrante)]:
                        vecinos_e_c.append(x)
            if len(vecinos_o_c) == 0:
                for x in vecinos_e_c:
                        vecinos_o_c.append(x)

            if (self.carga > 30 and self.charging == False and self.clean == False) :

                celdas_sucias = self.buscar_celdas_sucia(vecinos_o_c)

                if len(celdas_sucias) == 0:
                    self.seleccionar_nueva_pos(vecinos_o_c)
                else:
                    celda_a_limpiar = self.random.choice(celdas_sucias)
                    self.limpiar_una_celda(celda_a_limpiar)
            else:
                self.buscar_carga()

            self.list.append(self.pos)

            
            

    def advance(self):
        if self.pos != self.sig_pos:
            self.movimientos += 1

        if self.carga > 0 and self.clean == False:
            self.carga -= 1
            self.model.grid.move_agent(self, self.sig_pos)



class Habitacion(Model):
    def __init__(self, M: int, N: int,
                 num_agentes: int = 5,
                 porc_celdas_sucias: float = 0.6,
                 porc_muebles: float = 0.1,
                 num_carga: int = 4,
                 modo_pos_inicial: str = 'Fija',
                 ):

        self.num_agentes = num_agentes
        self.porc_celdas_sucias = porc_celdas_sucias
        self.porc_muebles = porc_muebles
        self.num_carga = num_carga

        cuadrantes = {
            "1": list(it.product(range(0,9), range(10,19))),
            "2": list(it.product(range(10,19), range(10,19))),
            "3": list(it.product(range(0,9), range(0,9))),
            "4": list(it.product(range(10,19), range(0,9)))
        }

        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]

        pos_inicial_carga = [(0,10), (9,0), (19,9), (10,19)]

        for id, pos in enumerate(pos_inicial_carga):
            carga = EstacionCarga(int(f"{num_agentes}1{id}") + 1, self)
            self.grid.place_agent(carga, pos)
            posiciones_disponibles.remove(pos)

        # Posicionamiento de muebles
        num_muebles = int(M * N * porc_muebles)
        posiciones_muebles = self.random.sample(posiciones_disponibles, k=num_muebles)

        for id, pos in enumerate(posiciones_muebles):
            mueble = Mueble(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(mueble, pos)
            posiciones_disponibles.remove(pos)

        # Posicionamiento de celdas sucias
        self.num_celdas_sucias = int(M * N * porc_celdas_sucias)
        posiciones_celdas_sucias = self.random.sample(
            posiciones_disponibles, k=self.num_celdas_sucias)

        for id, pos in enumerate(posiciones_disponibles):
            suciedad = pos in posiciones_celdas_sucias
            celda = Celda(int(f"{num_agentes}{id}") + 1, self, suciedad)
            self.grid.place_agent(celda, pos)

        # Posicionamiento de agentes robot
        if modo_pos_inicial == 'Aleatoria':
            pos_inicial_robots = self.random.sample(posiciones_disponibles, k=num_agentes)
        else:  # 'Fija'
            pos_inicial_robots = [(1, 1)] * num_agentes

        cuad = 1
        for id in range(num_agentes):
            robot = RobotLimpieza(id, self)
            robot.cuadrante = cuad
            self.grid.place_agent(robot, random.choice(cuadrantes[str(cuad)]))
            self.schedule.add(robot)
            cuad += 1
            if cuad > 4:
                cuad = 1

        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid, "Cargas": get_cargas,
                             "CeldasSucias": get_sucias},
        )

    def step(self):
        self.datacollector.collect(self)

        self.schedule.step()

    def todoLimpio(self):
        for (content, x, y) in self.grid.coord_iter():
            for obj in content:
                if isinstance(obj, Celda) and obj.sucia:
                    return False
        return True
    


def get_grid(model: Model) -> np.ndarray:
    """
    Método para la obtención de la grid y representarla en un notebook
    :param model: Modelo (entorno)
    :return: grid
    """
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        x, y = pos
        for obj in cell_content:
            if isinstance(obj, RobotLimpieza):
                grid[x][y] = 2
            elif isinstance(obj, Celda):
                grid[x][y] = int(obj.sucia)
    return grid


def get_cargas(model: Model):
    return [(agent.unique_id, agent.carga) for agent in model.schedule.agents]


def get_sucias(model: Model) -> int:
    """
    Método para determinar el número total de celdas sucias
    :param model: Modelo Mesa
    :return: número de celdas sucias
    """
    sum_sucias = 0
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Celda) and obj.sucia:
                sum_sucias += 1
    return sum_sucias 


def get_movimientos(agent: Agent) -> dict:
    if isinstance(agent, RobotLimpieza):
        return {agent.unique_id: agent.movimientos}
    # else:
    #    return 0




