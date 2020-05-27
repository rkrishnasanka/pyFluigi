import networkx as nx
from typing import Optional
from .net import Net
from .cell import Cell
from pyMINT.mintdevice import MINTDevice


class Layout:

    def __init__(self) -> None:
        self.cells = dict()
        self.nets = dict()
        self.G = nx.MultiDiGraph()
        self.__original_device = None
        self.__direct_map = []

    def applyLayout(self):
        device = self.__original_device
        for ID in self.__direct_map:
            component = device.getComponent(ID)
            cell = self.cells[ID]
            component.params.setParam("position", [cell.x, cell.y])
    
    
    def importMINTwithoutConstraints(self, device: Optional[MINTDevice]) -> None:
        
        self.__original_device = device
        
        for component in device.components:
            cell = Cell(component.ID, 0, 0, 1000, 1000)
            self.cells[cell.ID] = cell
            self.G.add_node(cell.ID)
            self.__direct_map.append(cell.ID)

        
        for connection in device.connections:
            net = Net(connection.ID, connection.source, connection.sinks)
            self.nets[net.ID] = net
            for sink in connection.sinks:
                self.G.add_edge(connection.source.component, sink.component)

    def importMINTwithConstraints(self, device: MINTDevice) -> None:
        #TODO: Process the constraints
        raise Exception('Not Implemented')