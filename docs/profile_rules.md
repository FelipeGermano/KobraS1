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
- preenchimento customizado;
- preco do kg de filamento;
- assistentes de calibracao desejados;
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
- Preenchimento customizado substitui o preenchimento do perfil quando habilitado.
- Custo estimado usa peso aproximado total e preco informado por kg.
- Comparacao resistencia x consumo calcula peso/custo para todos os niveis de resistencia.

## Assistentes de calibracao

### Temperatura

Gera faixas por material para torre de temperatura:

- PLA: 195 a 220 C;
- PETG: 225 a 250 C;
- ABS: 240 a 265 C;
- ASA: 245 a 270 C;
- TPU: 210 a 235 C.

### Flow ratio

Sugere testes de `0.92` a `1.04`, com `1.00` como ponto central. A recomendacao operacional e imprimir uma parede simples, medir a espessura real e ajustar proporcionalmente.

### Pressure advance

Sugere passos de `0.00` a `0.10`. A avaliacao e feita por linhas/cantos: escolher o menor valor que deixa cantos definidos sem subextrusao.

## Saidas

O perfil retorna parametros finais, avisos, custo, planos de calibracao, comparacao resistencia x consumo e justificativas (`decision_reasons`) para que o usuario entenda por que cada ajuste foi feito.
