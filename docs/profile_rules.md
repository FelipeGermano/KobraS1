# Motor de recomendacoes

## Entradas

O motor recebe:

- material;
- resistencia;
- qualidade;
- prioridade;
- finalidade;
- ambiente;
- exposicao a calor;
- necessidade de flexibilidade;
- direcao de esforco;
- permissao de suportes;
- quantidade de copias;
- bico utilizado;
- analise geometrica do modelo.

## Fontes de perfil

- `app/config/materials/materials.json`: temperaturas e ventilacao inicial por material.
- `app/config/processes/strength_quality.json`: paredes, preenchimento, topo/fundo e altura de camada.
- `app/config/printers/kobra_s1.json`: volume e bico padrao.

## Decisoes aplicadas

- Prioridade em resistencia aumenta paredes/preenchimento e reduz velocidade.
- Prioridade em velocidade aumenta camada/velocidade dentro do limite do bico.
- Prioridade visual reduz camada e velocidade.
- Economia reduz preenchimento sem ficar abaixo do minimo seguro.
- Uso funcional/externo eleva resistencia minima.
- PLA com calor/sol gera alerta.
- Uso externo alerta quando o material nao e ASA/PETG.
- TPU/flexibilidade limita velocidade e preenchimento.
- Esforco vertical/impacto aumenta paredes.
- Geometria com balancos habilita suporte quando o usuario permite.
- Material com maior risco de empenamento, base pequena ou modelo grande recomenda brim.

## Saidas

O perfil retorna parametros finais, avisos e justificativas (`decision_reasons`) para que o usuario entenda por que cada ajuste foi feito.

