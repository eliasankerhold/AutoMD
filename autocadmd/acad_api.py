from comtypes import client
import comtypes
import glob
import os


class Acad:
    """
    Interfaces the AutoCAD ActiveX API.

    :ivar app: ActiveX object of AutoCAD instance.
    :ivar doc: ActiveX object of active document.
    :ivar model: ActiveX object of active model space.

    :raise WindowsError: If no current AutoCAD instance is running.
    """
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
