# Arquitetura inicial

## Objetivo

O aplicativo e uma camada de assistencia para usuarios da Anycubic Kobra S1. Ele nao substitui o fatiador no MVP; ele valida o arquivo, coleta escolhas simples e gera um resumo tecnico seguro para orientar a abertura no Anycubic Slicer Next ou OrcaSlicer.

## Modulos principais

- `app/domain`: objetos de dominio, como impressora, material, analise de modelo e perfil de fatiamento.
- `app/services/model_import_service.py`: ponto unico de importacao. Aceita STL e 3MF, bloqueia G-code externo.
- `app/services/stl_service.py`: leitura de STL via `trimesh`.
- `app/services/three_mf_service.py`: leitura segura de 3MF via `zipfile` e `ElementTree`, extraindo somente geometria e metadados.
- `app/services/mesh_validation_service.py`: calculo de dimensoes, volume, area, componentes, problemas de malha e avisos.
- `app/services/profile_engine.py`: regras iniciais de material, resistencia, qualidade e prioridade.
- `app/services/report_service.py`: geracao de resumo JSON.
- `app/ui/main_window.py`: interface Tkinter do MVP.

## Regras de seguranca implementadas

- Arquivos `.gcode`, `.gco` e `.gc` sao bloqueados.
- 3MF e tratado como fonte de geometria, nao como fonte confiavel de perfil.
- Metadados de impressora/fatiador dentro do 3MF sao registrados e ignorados.
- Modelos acima de 250 x 250 x 250 mm sao marcados como erro.
- Problemas geometricos viram avisos compreensiveis no resumo.

## Limites atuais

- A analise de suporte e base e heuristica.
- Espessura de parede fina ainda e inferida por dimensao minima global.
- O MVP ainda nao gera G-code.
- A aplicacao ainda nao aplica perfil automaticamente no fatiador.

