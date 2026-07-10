from pathlib import Path
from zipfile import ZipFile


def main() -> None:
    output = Path("samples/foreign_printer_cube.3mf")
    output.parent.mkdir(exist_ok=True)
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
"""
    model = """<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <metadata name="Application">Foreign Slicer</metadata>
  <metadata name="Printer">Anycubic Kobra 2 Pro 0.4 nozzle</metadata>
  <resources>
    <object id="1" type="model">
      <mesh>
        <vertices>
          <vertex x="0" y="0" z="0"/>
          <vertex x="10" y="0" z="0"/>
          <vertex x="10" y="10" z="0"/>
          <vertex x="0" y="10" z="0"/>
          <vertex x="0" y="0" z="10"/>
          <vertex x="10" y="0" z="10"/>
          <vertex x="10" y="10" z="10"/>
          <vertex x="0" y="10" z="10"/>
        </vertices>
        <triangles>
          <triangle v1="0" v2="2" v3="1"/>
          <triangle v1="0" v2="3" v3="2"/>
          <triangle v1="4" v2="5" v3="6"/>
          <triangle v1="4" v2="6" v3="7"/>
          <triangle v1="0" v2="1" v3="5"/>
          <triangle v1="0" v2="5" v3="4"/>
          <triangle v1="1" v2="2" v3="6"/>
          <triangle v1="1" v2="6" v3="5"/>
          <triangle v1="2" v2="3" v3="7"/>
          <triangle v1="2" v2="7" v3="6"/>
          <triangle v1="3" v2="0" v3="4"/>
          <triangle v1="3" v2="4" v3="7"/>
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1"/>
  </build>
</model>
"""
    with ZipFile(output, "w") as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("3D/3dmodel.model", model)
    print(output)


if __name__ == "__main__":
    main()
