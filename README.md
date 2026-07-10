# Kobra S1 Assistant

Assistente inicial de fatiamento para a Anycubic Kobra S1.

Esta versao 0.1 entrega:

- leitura de arquivos STL;
- calculo de dimensoes, volume aproximado e area superficial;
- validacao contra o volume de impressao de 250 x 250 x 250 mm;
- perfis iniciais de PLA;
- regras de resistencia e qualidade;
- resumo de parametros em JSON;
- interface Tkinter simples.

## Como executar

```powershell
python -m app.main
```

## Testes

```powershell
python -m pytest
```

Se o `pytest` ainda nao estiver instalado:

```powershell
python -m pip install -e ".[dev]"
```

