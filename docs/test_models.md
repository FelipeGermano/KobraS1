# Modelos de teste

Os arquivos em `samples/` servem para testes manuais do MVP.

- `calibration_cube_ascii.stl`: cubo 20 x 20 x 20 mm em STL ASCII.
- `foreign_printer_cube.3mf`: cubo 10 x 10 x 10 mm com metadado de impressora estrangeira para validar que o app ignora configuracoes embutidas.

Comandos uteis:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m app.main
```

