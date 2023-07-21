from comtypes import client
import glob
import os

for pattern in ("acax*enu.tlb", "axdb*enu.tlb"):
    pattern = os.path.join(
        r"C:\Program Files\Common Files\Autodesk Shared",
        pattern
    )
    tlib = glob.glob(pattern)[0]
    client.GetModule(tlib)
    print(tlib)

import comtypes.gen.AutoCAD as ACAD

app = client.GetActiveObject('AutoCAD.Application', dynamic=True)
