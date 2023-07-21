from comtypes import client
import comtypes
import glob
import os


class Acad:
    def __init__(self):
        for pattern in ("acax*enu.tlb", "axdb*enu.tlb"):
            pattern = os.path.join(
                r"C:\Program Files\Common Files\Autodesk Shared",
                pattern
            )
            tlib = glob.glob(pattern)[0]
            client.GetModule(tlib)

        comtypes.npsupport.enable()

        try:
            self.app = client.GetActiveObject('AutoCAD.Application')
        except WindowsError:
            print('Make sure an AutoCAD instance is running.')

        self.doc = self.app.ActiveDocument
        self.model = self.doc.ModelSpace

        print(f'Working on document {self.doc.Name}')
