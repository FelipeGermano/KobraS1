# Plano de Desenvolvimento — Assistente de Fatiamento para Anycubic Kobra S1

## 1. Visão geral

Este projeto tem como objetivo criar uma aplicação simples para usuários iniciantes em impressão 3D, permitindo importar arquivos STL ou 3MF, escolher poucas opções de uso e gerar uma configuração segura e adequada para a impressora Anycubic Kobra S1.

A ferramenta deverá reduzir erros causados por:

- abertura de arquivos 3MF configurados para outras impressoras;
- escolha incorreta de material;
- temperaturas inadequadas;
- velocidade excessiva;
- número insuficiente de paredes;
- preenchimento incompatível com o uso da peça;
- orientação inadequada;
- falta de suportes;
- dimensões incompatíveis com a área de impressão;
- uso acidental de G-code criado para outra máquina.

A aplicação não substituirá completamente um fatiador. Ela funcionará como uma camada de assistência sobre o Anycubic Slicer Next ou OrcaSlicer.

---

## 2. Premissas iniciais

A primeira versão será desenvolvida com as seguintes premissas:

- sistema operacional principal: Windows;
- impressora: Anycubic Kobra S1;
- volume de impressão: 250 × 250 × 250 mm;
- bico padrão: 0,4 mm;
- fatiador utilizado como mecanismo: Anycubic Slicer Next ou OrcaSlicer;
- materiais iniciais:
  - PLA;
  - PETG;
  - ABS;
  - ASA;
  - TPU;
- entrada aceita:
  - STL;
  - 3MF;
- saída inicial:
  - arquivo de projeto 3MF compatível;
  - resumo das configurações aplicadas;
  - abertura automática no fatiador;
- saída futura:
  - G-code pronto para a Kobra S1.

---

## 3. Objetivo do produto

Permitir que o usuário escolha um modelo 3D e responda a perguntas simples, como:

- qual material será utilizado;
- qual o nível de resistência desejado;
- qual a qualidade desejada;
- se a peça ficará exposta ao sol ou calor;
- se a peça será decorativa ou funcional;
- em qual direção a peça receberá esforço;
- se o usuário aceita suportes;
- se deseja priorizar velocidade, qualidade ou resistência.

A aplicação converterá essas respostas em parâmetros técnicos de fatiamento.

---

## 4. Escopo do MVP

O MVP deverá executar as seguintes funções:

1. selecionar um arquivo STL ou 3MF;
2. identificar o tipo do arquivo;
3. impedir o uso direto de G-code desconhecido;
4. ler dimensões do modelo;
5. verificar se o modelo cabe na Kobra S1;
6. detectar escala potencialmente incorreta;
7. identificar malha inválida ou aberta;
8. calcular volume aproximado;
9. sugerir orientação básica;
10. receber escolhas simplificadas do usuário;
11. selecionar um perfil de impressão;
12. gerar um arquivo de configuração;
13. abrir o modelo no fatiador com o perfil correto;
14. exibir um resumo antes do fatiamento;
15. registrar avisos e recomendações.

---

## 5. Funcionalidades fora do MVP

As seguintes funcionalidades deverão ser implementadas somente após a validação da primeira versão:

- geração automática de G-code;
- envio direto para a impressora;
- integração com Anycubic Cloud;
- análise visual avançada da peça;
- posicionamento automático otimizado;
- criação automática de suportes pintados;
- cálculo estrutural por elementos finitos;
- análise automática da direção de esforço;
- reconhecimento de peças articuladas;
- gerenciamento de múltiplas impressoras;
- perfis personalizados por fabricante de filamento;
- histórico de impressões;
- aprendizado com avaliações do usuário;
- controle remoto da impressora;
- aplicativo móvel.

---

## 6. Perfis simplificados para o usuário

### 6.1 Nível de resistência

| Perfil | Paredes | Preenchimento | Topo e fundo | Padrão |
|---|---:|---:|---:|---|
| Decorativa | 2 | 8% | 3 camadas | Gyroid |
| Leve | 3 | 12% | 4 camadas | Gyroid |
| Uso comum | 3 | 15% | 4 camadas | Gyroid |
| Resistente | 4 | 25% | 5 camadas | Gyroid |
| Muito resistente | 5 ou 6 | 35% | 6 camadas | Gyroid |

Os valores deverão ser configuráveis no código e posteriormente em um painel administrativo.

### 6.2 Nível de qualidade

| Perfil | Altura de camada |
|---|---:|
| Rápida | 0,28 mm |
| Normal | 0,20 mm |
| Detalhada | 0,16 mm |
| Muito detalhada | 0,12 mm |

A altura máxima deverá respeitar o diâmetro do bico.

### 6.3 Prioridade

O usuário poderá selecionar:

- economia de material;
- equilíbrio;
- resistência;
- qualidade visual;
- velocidade.

A prioridade influenciará:

- paredes;
- preenchimento;
- velocidade;
- altura de camada;
- suportes;
- topo e fundo;
- tempo estimado.

---

## 7. Regras iniciais por material

Os valores abaixo deverão funcionar como pontos de partida e não como calibração definitiva.

### PLA

- temperatura inicial do bico: 210 °C;
- mesa: 60 °C;
- ventilação elevada após as primeiras camadas;
- indicado para:
  - decoração;
  - protótipos;
  - peças de uso interno;
- alerta:
  - não recomendado para calor elevado;
  - pode deformar dentro de veículos ou sob sol intenso.

### PETG

- temperatura inicial do bico: 240 °C;
- mesa: 75 °C;
- ventilação moderada;
- indicado para:
  - peças funcionais;
  - ambientes úmidos;
  - maior resistência térmica que PLA;
- alerta:
  - pode gerar fios;
  - exige filamento seco;
  - pode aderir excessivamente à mesa.

### ABS

- temperatura inicial do bico: 255 °C;
- mesa: 100 °C;
- câmara fechada;
- indicado para:
  - peças técnicas;
  - resistência térmica;
- alerta:
  - exige ventilação adequada do ambiente;
  - maior risco de empenamento;
  - não utilizar com a porta aberta durante a impressão.

### ASA

- temperatura inicial do bico: 260 °C;
- mesa: 100 °C;
- câmara fechada;
- indicado para:
  - uso externo;
  - exposição UV;
- alerta:
  - risco de empenamento;
  - exige ambiente ventilado.

### TPU

- temperatura inicial do bico: 225 °C;
- mesa: 50 °C;
- velocidade reduzida;
- indicado para:
  - peças flexíveis;
  - amortecimento;
- alerta:
  - alimentação de filamento mais sensível;
  - retração deve ser conservadora;
  - filamento úmido prejudica muito o resultado.

---

## 8. Fluxo principal da aplicação

### Etapa 1 — Importação

O usuário seleciona um arquivo STL ou 3MF.

A aplicação deve:

- validar a extensão;
- validar se o arquivo pode ser lido;
- calcular dimensões;
- identificar unidades prováveis;
- verificar se o modelo possui escala suspeita;
- verificar se o modelo cabe na impressora.

### Etapa 2 — Análise do modelo

A aplicação deve verificar:

- largura;
- profundidade;
- altura;
- volume;
- quantidade de componentes;
- malha aberta;
- faces invertidas;
- geometrias não-manifold;
- espessuras potencialmente muito finas;
- base de contato com a mesa;
- ângulos com provável necessidade de suporte.

### Etapa 3 — Perguntas ao usuário

Campos recomendados:

- material;
- finalidade;
- nível de resistência;
- nível de qualidade;
- prioridade;
- uso interno ou externo;
- exposição a calor;
- necessidade de flexibilidade;
- direção do esforço;
- permitir suportes;
- quantidade de cópias;
- bico utilizado.

### Etapa 4 — Seleção do perfil

O sistema deverá combinar:

- perfil da impressora;
- perfil do material;
- perfil de processo;
- regras específicas do modelo;
- opções escolhidas pelo usuário.

### Etapa 5 — Validação

Antes de gerar a saída, o sistema deve exibir:

- impressora selecionada;
- bico;
- material;
- temperatura;
- altura de camada;
- paredes;
- preenchimento;
- suporte;
- brim;
- orientação;
- avisos;
- incompatibilidades.

### Etapa 6 — Geração

Na primeira versão:

- gerar um arquivo JSON ou configuração compatível;
- salvar uma cópia do modelo;
- abrir no Anycubic Slicer Next ou OrcaSlicer;
- orientar o usuário a conferir a pré-visualização;
- deixar o fatiamento final sob controle do usuário.

Na versão automática:

- executar o fatiador por linha de comando;
- gerar G-code;
- analisar os metadados do resultado;
- validar dimensões e temperaturas;
- disponibilizar o arquivo final.

---

## 9. Arquitetura proposta

### 9.1 Tecnologias

- linguagem: Python 3.12 ou superior;
- interface:
  - primeira versão: Tkinter;
  - alternativa futura: PySide6;
- análise de malha:
  - trimesh;
  - numpy;
- leitura de 3MF:
  - zipfile;
  - xml.etree.ElementTree;
  - bibliotecas adicionais, se necessário;
- validação geométrica:
  - trimesh;
  - pymeshfix, opcional;
- configurações:
  - JSON;
  - YAML, opcional;
- logs:
  - logging nativo do Python;
- testes:
  - pytest;
- empacotamento:
  - PyInstaller;
- integração com fatiador:
  - subprocess;
  - linha de comando do OrcaSlicer;
- persistência:
  - JSON no MVP;
  - SQLite em versões posteriores.

### 9.2 Organização de pastas

```text
kobra-s1-assistant/
├── app/
│   ├── main.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── import_view.py
│   │   ├── profile_view.py
│   │   └── result_view.py
│   ├── domain/
│   │   ├── model_analysis.py
│   │   ├── slicing_profile.py
│   │   ├── material.py
│   │   └── printer.py
│   ├── services/
│   │   ├── stl_service.py
│   │   ├── three_mf_service.py
│   │   ├── mesh_validation_service.py
│   │   ├── profile_engine.py
│   │   ├── slicer_service.py
│   │   └── report_service.py
│   ├── rules/
│   │   ├── strength_rules.py
│   │   ├── support_rules.py
│   │   ├── orientation_rules.py
│   │   └── adhesion_rules.py
│   └── config/
│       ├── printers/
│       ├── materials/
│       └── processes/
├── tests/
├── docs/
├── samples/
├── logs/
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 10. Componentes do sistema

### 10.1 Importador STL

Responsabilidades:

- ler o arquivo;
- validar malha;
- calcular dimensões;
- calcular volume;
- calcular área superficial;
- detectar múltiplos corpos;
- detectar escala suspeita;
- retornar um objeto padronizado.

### 10.2 Importador 3MF

Responsabilidades:

- abrir o contêiner ZIP;
- localizar o modelo;
- extrair geometria;
- identificar metadados;
- identificar configurações de impressão;
- ignorar configurações de outras impressoras;
- preservar somente informações seguras:
  - geometria;
  - nomes;
  - cores;
  - posicionamento, quando aplicável.

O sistema não deverá assumir que configurações contidas no 3MF são adequadas à Kobra S1.

### 10.3 Analisador de malha

Responsabilidades:

- verificar se a malha é fechada;
- verificar se é manifold;
- localizar faces degeneradas;
- detectar normais invertidas;
- identificar paredes finas;
- identificar modelo sem base adequada;
- classificar a gravidade dos problemas.

### 10.4 Motor de perfis

O motor receberá:

- impressora;
- bico;
- material;
- resistência;
- qualidade;
- prioridade;
- análise geométrica.

O motor retornará:

- altura de camada;
- largura de linha;
- número de paredes;
- preenchimento;
- padrão de preenchimento;
- camadas superiores e inferiores;
- temperaturas;
- velocidade;
- aceleração;
- retração;
- ventilação;
- brim;
- suportes;
- alertas.

### 10.5 Motor de orientação

Versão inicial baseada em regras:

- priorizar maior área plana na mesa;
- reduzir altura total;
- minimizar balanços;
- evitar que o esforço principal atravesse linhas de camada;
- evitar grandes pontes;
- minimizar suportes;
- respeitar acabamento visual.

A aplicação deverá permitir que o usuário mantenha a orientação original.

### 10.6 Integração com o fatiador

Responsabilidades:

- localizar a instalação;
- validar versão;
- preparar arquivos de perfil;
- executar comandos;
- capturar erros;
- abrir o projeto;
- futuramente gerar G-code.

### 10.7 Gerador de relatório

O relatório deverá conter:

- arquivo original;
- data e hora;
- impressora;
- material;
- configurações escolhidas;
- dimensões;
- peso estimado;
- avisos;
- recomendações;
- parâmetros finais.

---

## 11. Regras de segurança

A aplicação deverá:

- bloquear G-code cuja origem não seja confirmada;
- não reutilizar start G-code de outra impressora;
- não gerar movimentos fora do volume da Kobra S1;
- respeitar limites de temperatura;
- alertar sobre materiais que exigem ventilação;
- alertar sobre ABS e ASA em ambientes fechados sem ventilação;
- impedir seleção de temperatura incompatível com o material;
- impedir perfil de bico diferente do bico informado;
- exigir confirmação antes de gerar G-code;
- recomendar análise da pré-visualização;
- gerar logs das configurações utilizadas.

---

## 12. Fases de desenvolvimento

## Fase 0 — Pesquisa e preparação

### Objetivos

- confirmar o formato dos perfis do fatiador;
- testar a linha de comando do OrcaSlicer;
- identificar arquivos oficiais da Kobra S1;
- criar modelos de teste;
- documentar parâmetros iniciais.

### Entregáveis

- documento de arquitetura;
- repositório inicial;
- perfis de referência;
- lista de comandos suportados;
- conjunto inicial de arquivos STL e 3MF para testes.

### Critérios de aceite

- perfil da Kobra S1 identificado;
- fatiador executado localmente;
- arquivo de teste aberto pelo sistema;
- configuração de exemplo carregada sem erro.

---

## Fase 1 — Importação e análise

### Objetivos

- importar STL;
- importar geometria de 3MF;
- ler dimensões;
- verificar compatibilidade com o volume;
- validar malha.

### Entregáveis

- importador STL;
- importador 3MF;
- analisador geométrico;
- relatório técnico básico.

### Critérios de aceite

- arquivos válidos são importados;
- arquivos inválidos geram mensagem compreensível;
- dimensões são calculadas corretamente;
- modelos maiores que 250 × 250 × 250 mm são identificados;
- configurações de impressoras estrangeiras não são aplicadas.

---

## Fase 2 — Interface do MVP

### Objetivos

Criar uma interface simples com:

- botão para selecionar arquivo;
- visualização das dimensões;
- seleção de material;
- seleção de resistência;
- seleção de qualidade;
- seleção de prioridade;
- opção de suportes;
- resumo final.

### Entregáveis

- aplicativo navegável;
- validação dos campos;
- mensagens de erro;
- tela de resumo.

### Critérios de aceite

- usuário consegue concluir o fluxo sem editar arquivos;
- campos obrigatórios são validados;
- configurações finais são exibidas;
- interface funciona em Windows.

---

## Fase 3 — Motor de recomendações

### Objetivos

- implementar regras de resistência;
- implementar regras de material;
- implementar regras de qualidade;
- implementar regras de aderência;
- implementar recomendações de suporte.

### Entregáveis

- perfis JSON;
- motor de regras;
- testes automatizados;
- resumo das decisões tomadas.

### Critérios de aceite

- cada combinação gera resultado previsível;
- perfis inválidos são rejeitados;
- parâmetros respeitam limites da impressora;
- as escolhas do usuário influenciam o resultado.

---

## Fase 4 — Integração com fatiador

### Objetivos

- localizar Anycubic Slicer Next ou OrcaSlicer;
- carregar perfil da Kobra S1;
- enviar modelo e configurações;
- abrir projeto no fatiador.

### Entregáveis

- serviço de integração;
- configuração do caminho do fatiador;
- tratamento de erros;
- registro de execução.

### Critérios de aceite

- modelo abre com a impressora correta;
- perfil da Kobra S1 é aplicado;
- perfil do material é aplicado;
- configurações externas do 3MF são ignoradas;
- usuário consegue fatiar manualmente.

---

## Fase 5 — Versão automática

### Objetivos

- executar o fatiamento por linha de comando;
- gerar G-code;
- extrair tempo e consumo;
- validar o arquivo gerado.

### Entregáveis

- geração automática;
- relatório final;
- arquivo pronto para transferência.

### Critérios de aceite

- G-code utiliza a Kobra S1;
- dimensões não ultrapassam os limites;
- temperaturas correspondem ao perfil;
- tempo e material são apresentados;
- erros de fatiamento são tratados.

---

## Fase 6 — Empacotamento e distribuição

### Objetivos

- gerar instalador para Windows;
- incluir configurações padrão;
- criar assistente de instalação;
- criar documentação.

### Entregáveis

- arquivo executável;
- instalador;
- manual do usuário;
- manual técnico;
- licença;
- changelog.

### Critérios de aceite

- instalação em máquina limpa;
- inicialização sem Python instalado;
- detecção do fatiador;
- criação de logs;
- desinstalação correta.

---

## 13. Cronograma sugerido

| Fase | Duração estimada |
|---|---:|
| Pesquisa e preparação | 1 semana |
| Importação e análise | 2 semanas |
| Interface do MVP | 1 a 2 semanas |
| Motor de recomendações | 2 semanas |
| Integração com fatiador | 2 semanas |
| Testes do MVP | 1 semana |
| Versão automática | 2 a 3 semanas |
| Empacotamento | 1 semana |

Estimativa total para uma primeira versão utilizável:

**9 a 12 semanas**, dependendo da disponibilidade da linha de comando e dos formatos de perfil do fatiador.

---

## 14. Estratégia de testes

### 14.1 Testes unitários

Testar:

- cálculo de dimensões;
- seleção de perfis;
- regras de resistência;
- regras de temperatura;
- detecção de arquivo inválido;
- validação do volume;
- geração de configurações.

### 14.2 Testes de integração

Testar:

- abertura no fatiador;
- carregamento do perfil;
- execução por linha de comando;
- geração do projeto;
- geração futura de G-code.

### 14.3 Testes físicos

Criar um conjunto de peças padrão:

1. cubo de calibração;
2. Benchy;
3. teste de overhang;
4. teste de ponte;
5. torre de temperatura;
6. teste de retração;
7. peça funcional com parafuso;
8. gancho submetido a esforço;
9. peça alta e estreita;
10. peça grande para testar empenamento.

### 14.4 Matriz de testes

Executar os testes com:

- PLA;
- PETG;
- ABS;
- ASA;
- TPU;
- perfis decorativo, comum e resistente;
- qualidade rápida, normal e detalhada.

---

## 15. Critérios gerais de aceite do MVP

O MVP será considerado pronto quando:

- importar STL e 3MF;
- analisar dimensões;
- identificar modelos incompatíveis;
- ignorar perfis de outras impressoras;
- aceitar escolhas simplificadas;
- gerar um perfil seguro;
- abrir o modelo no fatiador;
- aplicar a Kobra S1;
- apresentar configurações finais;
- gerar alertas compreensíveis;
- funcionar em Windows;
- possuir testes básicos;
- possuir documentação mínima.

---

## 16. Riscos do projeto

### Perfil do fatiador mudar

Mitigação:

- manter integração isolada;
- versionar perfis;
- criar adaptadores por versão.

### Linha de comando limitada

Mitigação:

- manter a primeira versão com abertura assistida;
- gerar 3MF de projeto;
- não depender inicialmente de geração automática.

### Análise de orientação imprecisa

Mitigação:

- tratar como recomendação;
- pedir confirmação;
- permitir comparação de orientações.

### Configurações universais de material falharem

Mitigação:

- indicar que são valores iniciais;
- permitir ajuste por fabricante;
- adicionar calibração guiada.

### Modelo 3MF complexo

Mitigação:

- extrair somente geometria no MVP;
- avisar quando elementos não forem preservados;
- manter cópia do arquivo original.

### G-code inseguro

Mitigação:

- usar somente perfil oficial;
- validar limites;
- manter geração automática fora do MVP;
- exigir confirmação.

---

## 17. Melhorias futuras

- assistente de calibração de temperatura;
- assistente de flow ratio;
- assistente de pressure advance;
- cadastro de marcas de filamento;
- leitura de QR Code do rolo;
- perfis por cor e lote;
- comparação entre resistência e consumo;
- estimativa de custo;
- armazenamento do histórico;
- recomendação baseada em impressões anteriores;
- integração com câmera;
- detecção de falhas durante a impressão;
- envio direto para a Kobra S1;
- suporte ao ACE Pro;
- suporte multicolorido;
- suporte a outros diâmetros de bico;
- suporte a outras impressoras Anycubic;
- versão web;
- versão móvel.

---

## 18. Primeira lista de tarefas técnicas

### Configuração inicial

- [x] Criar repositório Git.
- [ ] Criar ambiente virtual.
- [x] Configurar `pyproject.toml`.
- [ ] Instalar `trimesh`, `numpy` e `pytest`.
- [x] Criar estrutura de pastas.
- [ ] Configurar logging.
- [ ] Definir padrões de código.
- [ ] Criar pipeline de testes.

### Modelos e arquivos

- [x] Implementar leitura de STL.
- [ ] Implementar leitura de 3MF.
- [ ] Extrair geometria do 3MF.
- [ ] Detectar metadados de impressora.
- [ ] Ignorar configurações incompatíveis.
- [x] Calcular dimensões.
- [x] Calcular volume.
- [ ] Validar malha.

### Perfis

- [x] Criar perfil da Anycubic Kobra S1.
- [x] Criar perfil do bico de 0,4 mm.
- [x] Criar perfil PLA.
- [x] Criar perfil PETG.
- [x] Criar perfil ABS.
- [x] Criar perfil ASA.
- [x] Criar perfil TPU.
- [x] Criar níveis de resistência.
- [x] Criar níveis de qualidade.

### Interface

- [x] Criar tela inicial.
- [x] Criar seletor de arquivo.
- [x] Criar formulário de uso.
- [ ] Criar tela de análise.
- [x] Criar tela de resumo.
- [ ] Criar tela de erros.
- [ ] Criar configurações do aplicativo.

### Integração

- [ ] Localizar instalação do fatiador.
- [ ] Configurar caminho manual.
- [ ] Testar comandos disponíveis.
- [ ] Criar adaptador do fatiador.
- [ ] Abrir modelo com perfil.
- [ ] Capturar erros do processo.
- [ ] Registrar saída em log.

### Testes

- [ ] Criar arquivos de teste.
- [x] Criar testes unitários.
- [ ] Criar testes de integração.
- [ ] Executar testes físicos.
- [ ] Registrar resultados.
- [ ] Ajustar perfis.

---

## 19. Definição de versão

### Versão 0.1

- importação STL;
- análise de dimensões;
- perfis PLA;
- resistência e qualidade;
- resumo de parâmetros.

### Versão 0.2

- importação 3MF;
- validação de malha;
- perfis PETG;
- alertas de suporte e aderência.

### Versão 0.3

- integração com OrcaSlicer;
- abertura automática;
- perfil Kobra S1;
- relatório.

### Versão 0.5

- suporte a ABS, ASA e TPU;
- instalador Windows;
- histórico básico.

### Versão 1.0

- geração automática de G-code;
- validação final;
- documentação completa;
- conjunto de testes físicos aprovado.

---

## 20. Resultado esperado

Ao final do projeto, o usuário deverá conseguir:

1. abrir o aplicativo;
2. escolher um STL ou 3MF;
3. informar o material;
4. selecionar a finalidade da peça;
5. escolher resistência e qualidade;
6. receber alertas sobre problemas;
7. visualizar os parâmetros aplicados;
8. abrir o projeto corretamente configurado;
9. fatiar para a Anycubic Kobra S1;
10. reduzir significativamente impressões ruins causadas por configurações inadequadas.

A ferramenta deverá esconder a complexidade do fatiamento sem impedir que usuários mais avançados revisem ou alterem os parâmetros finais.
