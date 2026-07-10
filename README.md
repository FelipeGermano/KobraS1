# Kobra S1 Assistant

Assistente inicial de fatiamento para a Anycubic Kobra S1.

Esta versao 0.1 entrega:

- leitura de arquivos STL e 3MF;
- bloqueio de G-code externo;
- calculo de dimensoes, volume aproximado, area superficial e componentes;
- validacao basica de malha: aberta, nao-manifold, faces degeneradas e orientacao;
- validacao contra o volume de impressao de 250 x 250 x 250 mm;
- deteccao e ignorancia de metadados de impressora vindos de 3MF;
- perfis iniciais de PLA, PETG, ABS, ASA e TPU;
- regras de resistencia e qualidade;
- resumo de parametros em JSON;
- exportacao de projeto 3MF com perfil recomendado embutido;
- abertura do projeto no Anycubic Slicer Next;
- geracao automatica de G-code quando o CLI do slicer aceita o modelo;
- interface Tkinter com abas de analise, perfil, erros e configuracoes.

## Ambiente local

Um ambiente virtual pode ser criado com:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Neste workspace, o `.venv` ja foi criado para teste local.

## Como executar

```powershell
.\.venv\Scripts\python.exe -m app.main
```

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Documentacao

- `docs/architecture.md`: arquitetura inicial e regras de seguranca.
- `docs/slicer_research.md`: pesquisa local do Anycubic Slicer Next.
- `docs/test_models.md`: arquivos de amostra para testes manuais.
- `docs/profile_rules.md`: regras atuais do motor de recomendacoes.
- `docs/slicer_integration.md`: integracao com Anycubic Slicer Next e G-code.

## Amostras

- `samples/calibration_cube_ascii.stl`
- `samples/foreign_printer_cube.3mf`

## Exportacao 3MF

O botao `Exportar 3MF com perfil` gera um projeto `.3mf` com:

- geometria do STL ou 3MF original;
- `Metadata/project_settings.config` com parametros recomendados para a Kobra S1;
- `Metadata/kobra_s1_summary.json` com o resumo completo das decisoes.

Abra o arquivo exportado no slicer e confira a pre-visualizacao antes de imprimir.

## G-code automatico

O botao `Gerar G-code` usa o Anycubic Slicer Next por linha de comando. Quando o slicer gera o arquivo, o assistente valida temperaturas e movimentos antes de marcar o resultado como valido.

Alguns 3MF complexos podem fazer a CLI do slicer falhar mesmo abrindo normalmente na interface grafica. Nesses casos, use `Abrir no slicer` e faça o fatiamento manual.
