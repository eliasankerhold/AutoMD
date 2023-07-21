from comtypes import client
import comtypes
import glob
import os
import numpy as np
from array import array

for pattern in ("acax*enu.tlb", "axdb*enu.tlb"):
    pattern = os.path.join(
        r"C:\Program Files\Common Files\Autodesk Shared",
        pattern
    )
    tlib = glob.glob(pattern)[0]
    client.GetModule(tlib)
    print(tlib)

# import comtypes.gen.AutoCAD as ACAD

comtypes.npsupport.enable()

app = client.GetActiveObject('AutoCAD.Application', dynamic=True)
doc = app.ActiveDocument
model = doc.ModelSpace
print(doc.Name)

p1 = np.array([0, 0, 0], dtype='float64')
p2 = np.array([1, 1, 0], dtype='float64')
p3 = np.array([2, 2, 0], dtype='float64')

l1 = np.array([p1, p2, p3], dtype='float64').flatten()
print(l1)

model.AddPolyline(l1)
