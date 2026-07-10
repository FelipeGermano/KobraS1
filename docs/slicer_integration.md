# Integracao com fatiador

## Fase 4

Implementado:

- deteccao da instalacao local do Anycubic Slicer Next;
- validacao do executavel usando `--help`;
- resolucao dos perfis oficiais da Anycubic Kobra S1 0.4 mm;
- abertura de projeto 3MF no slicer;
- captura de stdout, stderr, exit code e arquivos gerados;
- configuracao manual do caminho do slicer pela interface.

Instalacao testada:

```text
C:\Program Files\AnycubicSlicerNext\AnycubicSlicerNext.exe
```

Versao observada:

```text
AnycubicSlicerNext-1.4.1.2
```

## Fase 5

Implementado:

- exportacao automatica de um 3MF recomendado antes do fatiamento;
- execucao do slicer por CLI com `--slice 0`;
- carregamento dos perfis oficiais com `--load-settings` e `--load-filaments`;
- deteccao do G-code gerado;
- validacao basica do G-code:
  - temperaturas de bico e mesa;
  - limites de movimento com margem para purge/apresentacao do perfil oficial;
  - tempo e filamento quando os metadados existem.

## Resultado dos testes locais

O cubo `samples/calibration_cube_ascii.stl` gera G-code com sucesso:

```text
plate_1.gcode
tempo estimado: 14m 32s
temperaturas detectadas: bico 205 C, mesa 55 C
```

O arquivo complexo `spray_can.3mf` e analisado/exportado corretamente pelo assistente, mas a CLI do Anycubic Slicer Next encerra via crash reporter durante o fatiamento automatico. A aplicacao captura esse erro e mostra os logs na aba `Erros`.

Nesse caso, o fluxo recomendado e usar `Exportar 3MF com perfil` ou `Abrir no slicer` e fatiar manualmente pela interface do slicer.

