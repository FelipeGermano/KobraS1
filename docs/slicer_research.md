# Pesquisa local do fatiador

Data da verificacao: 2026-07-10.

## Instalacao encontrada

- Anycubic Slicer Next: `C:\Program Files\AnycubicSlicerNext`
- Executavel principal: `C:\Program Files\AnycubicSlicerNext\AnycubicSlicerNext.exe`
- Versao reportada no CLI: `AnycubicSlicerNext-1.4.1.2`

## Comando de ajuda testado

```powershell
& "C:\Program Files\AnycubicSlicerNext\AnycubicSlicerNext.exe" --help
```

O comando retornou codigo `0` e lista opcoes para abrir arquivos `.3mf` e `.stl`, exportar projeto 3MF, carregar configuracoes e carregar filamentos.

Opcoes relevantes para fases futuras:

- `--load-settings "setting1.json;setting2.json"`
- `--load-filaments "filament1.json;filament2.json;..."`
- `--export-3mf filename.3mf`
- `--export-settings settings.json`
- `--slice option`
- `--outputdir dir`
- `--info`
- `--skip-modified-gcodes option`

Prioridade declarada pelo CLI:

1. valores da linha de comando;
2. valores carregados com `--load-settings` e `--load-filaments`;
3. valores vindos do 3MF.

Essa prioridade confirma a estrategia do MVP: carregar perfis seguros por fora e tratar configuracoes internas do 3MF como baixa confianca.

## Perfis oficiais encontrados

Perfil de maquina da Kobra S1 com bico 0,4 mm:

```text
C:\Program Files\AnycubicSlicerNext\resources\profiles\Anycubic\machine\Anycubic Kobra S1 0.4 nozzle.json
```

Campos observados:

- `printer_model`: `Anycubic Kobra S1`
- `printer_variant`: `0.4`
- `nozzle_diameter`: `0.4`
- `printable_area`: 250 x 250 mm
- `printable_height`: 250 mm
- `gcode_flavor`: `klipper`
- `default_print_profile`: `0.20mm Standard @Anycubic Kobra S1 0.4 nozzle`
- `default_filament_profile`: `Anycubic PLA @Anycubic Kobra S1 0.4 nozzle`

Perfis tambem existem para bicos 0,25, 0,6 e 0,8 mm.

## Decisoes para implementacao

- Manter o perfil interno da Kobra S1 em JSON simples no MVP.
- Na Fase 4, usar os perfis oficiais do Anycubic Slicer Next quando a instalacao local estiver disponivel.
- Nao reutilizar start/end G-code vindo de arquivos 3MF importados.
- Usar `--help`, `--info`, `--load-settings`, `--load-filaments` e `--export-3mf` como base inicial da integracao futura.

