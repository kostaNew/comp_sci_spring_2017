import numpy as np
import pandas as pd
from vtk import *
from vtk.util import numpy_support
import imp
import h5py

from sklearn.neighbors import KDTree
import os
from tqdm import tqdm

class MeshLoad:
    
    def __init__(self, filename, mesh_type='tet'):
        
        assert(os.path.exists(filename))
        assert(mesh_type == 'tri' or mesh_type == 'tet')
        self.filename = filename
        self.mesh_type = mesh_type
        self.cells_array = None
        self.points_array = None

    def update(self):
        
        reader = vtkUnstructuredGridReader()
        reader.SetFileName(self.filename)
        reader.Update()
        
        self.data = data = reader.GetOutput()
        points = data.GetPoints()
        cells = data.GetCells()
        
        points_array = numpy_support.vtk_to_numpy(points.GetData())
        cells_array = numpy_support.vtk_to_numpy(cells.GetData())

        j = 0
        lst = []
        edges = []
        size_ = 3 if self.mesh_type == 'tri' else 4

        while j < len(cells_array):
            if  cells_array[j] == 2:
                edges.append([cells_array[j+1], cells_array[j+2]])
            elif cells_array[j] == size_:
                if size_ == 3:
                    lst.append([cells_array[j+1], cells_array[j+2], cells_array[j+3]])
                elif size_ == 4:
                    lst.append([cells_array[j+1], cells_array[j+2], cells_array[j+3], cells_array[j+4]])
            j += cells_array[j] + 1
            
        self.cells_array = np.array(lst)
        self.points_array = points_array[:,:-1] if self.mesh_type == 'tri' else points_array
        self.edges_array = np.array(edges)
        
    def write_result(self, full_x):
        array_for_write = numpy_support.numpy_to_vtk(full_x, deep=True, array_type=vtk.VTK_FLOAT)
        array_for_write.SetName("result") 
        self.data.GetPointData().AddArray(array_for_write)

        writer = vtkXMLUnstructuredGridWriter()
        writer.SetFileName('result.vtu')
        writer.SetInputData(self.data)

        writer.Write()