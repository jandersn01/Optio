

|  |
| ----- |
| Proposta de Projeto    Optio  |
|  |
| **24/02/2026** |

**Histórico de Revisões**

| Revisão | Data | Autor | Descrição |
| :---: | :---: | :---: | :---: |
| 1.0 | 24/02/2026 | Equipe Optio | Versão inicial da proposta |
| 1.1 | 07/04/2026 | Maria Eduarda Vitorino | Revisão: reposicionamento competitivo, arquitetura de coleta (Firecrawl + LLM como parser), Módulo 6 redefinido como Alertas Salvos, orçamento de APIs atualizado com três cenários, IFPUG ampliado para 99 PF, equipe atualizada |



**Conteúdo**

[1\.	Sobre o documento	](#sobre-o-documento)

[2\.	Contexto, descrição do Problema/Motivação	](#contexto/descrição-do-problema/motivação)

[3\.	Objetivos do Projeto	](#objetivos-do-projeto)

[4\.	Detalhamento do Escopo	](#detalhamento-do-escopo)

[5\.	Processo de Desenvolvimento	](#processo-de-desenvolvimento)

[6\.	Restrições	](#restrições)

[7\.	Premissas	](#premissas)

[8\.	Riscos	](#riscos)

[9\.	Estimativa de Tamanho	](#estimativa-de-tamanho)

[10\.	Cronograma 	](#cronograma)

[11\.	Equipe	](#equipe)

[12\.	Orçamento	](#orçamento)

1. #  **Sobre o documento** 

O presente documento constitui a proposta técnica do projeto **Optio**. Estão aqui definidos o escopo, as especificações funcionais e o planejamento para o desenvolvimento de um sistema de pesquisa e agregação de informações sobre cursos de pós-graduação. A finalidade deste documento é descrever o produto de software a ser desenvolvido, suas funcionalidades e os critérios que orientarão sua execução.

2. # **Contexto/Descrição do Problema/Motivação** 

  A decisão sobre a continuidade da formação acadêmica é um momento crítico na trajetória de qualquer profissional. Seja ao término da graduação ou em um momento de transição na carreira, a pergunta sobre qual caminho seguir — e como se qualificar para isso — é recorrente e muitas vezes difícil de responder. A dificuldade, nesse contexto, não está na ausência de informação, mas em sua dispersão: dados sobre cursos de pós-graduação estão fragmentados em múltiplas fontes, sem um ponto centralizado de consulta, o que dificulta a comparação de opções e prejudica uma tomada de decisão fundamentada.

Esse cenário é ainda mais desafiador quando o critério financeiro entra em jogo. Cursos de pós-graduação gratuitos existem em todo o Brasil — oferecidos por instituições públicas, programas governamentais e iniciativas de fomento à educação —, mas localizar essas oportunidades exige do interessado uma pesquisa extensa, dispersa e frequentemente incompleta.

O **Optio** surge como resposta a esse problema. Trata-se de um sistema de pesquisa capaz de reunir e apresentar informações sobre cursos de pós-graduação **gratuitos** oferecidos em todo o Brasil, nas modalidades presencial e EAD, filtrando resultados de acordo com a área de interesse do usuário ou por palavras-chave por ele informadas. A obtenção dessas informações será realizada por meio de uma abordagem híbrida de coleta de dados, cujos detalhes técnicos estão descritos na seção de arquitetura do sistema.

O nome *Optio*, do latim, significa *escolha*, *opção*, *liberdade de decidir* — um posicionamento que reflete diretamente o propósito do produto: oferecer ao usuário o embasamento necessário para que sua decisão sobre o próximo passo acadêmico ou profissional seja segura e bem-informada.

3. # **Objetivos do Projeto** 
**3.1 Objetivo Geral**

Desenvolver o **Optio**, um sistema web que centraliza e entrega, de forma personalizada, informações sobre cursos de pós-graduação gratuitos oferecidos em todo o território nacional, nas modalidades presencial e EAD, reduzindo o esforço e o tempo despendido pelo usuário na pesquisa dessas oportunidades.

---

**3.2 Objetivos Específicos**

Os objetivos específicos do projeto são definidos segundo o critério S.M.A.R.T — isto é, são específicos, mensuráveis, atingíveis, relevantes e temporalmente delimitados.

**a) Confirmação de solicitação em tempo hábil** O sistema deve confirmar o recebimento de cada solicitação de busca em até **4 segundos** após o envio, garantindo ao usuário retorno imediato sobre o processamento da sua requisição, com entrega dos resultados realizada de forma assíncrona via e-mail. Meta a ser atingida até **junho de 2026**.

**b) Relevância dos resultados** Pelo menos **80% dos resultados** retornados pelo sistema devem ser pertinentes à área de interesse ou às palavras-chave informadas pelo usuário. A aferição será realizada por meio de um protocolo formal de avaliação, definido antes da Sprint 2, composto por: (a) amostra mínima de 30 buscas com critérios variados; (b) avaliação independente por ao menos 2 membros da equipe não envolvidos na coleta; (c) rubrica de relevância com critério binário (pertinente / não pertinente) baseado na correspondência entre a área/palavras-chave da busca e o conteúdo do curso retornado. O resultado final é calculado como precision (resultados pertinentes / total retornado). Meta a ser atingida até **junho de 2026**.

**c) Cobertura nacional** O sistema deve ser capaz de indexar e retornar cursos de pós-graduação gratuitos de instituições localizadas em todos os **27 estados** do Brasil, contemplando ambas as modalidades: presencial e EAD. Meta a ser atingida até **junho de 2026**.

**d) Cobertura de resultados por busca** O sistema deve retornar todos os cursos aderentes aos critérios informados pelo usuário, sem limite mínimo imposto — podendo retornar zero resultados quando nenhuma oferta corresponder à pesquisa, comunicando essa ausência de forma clara ao usuário. Meta a ser atingida até **junho de 2026**.

4. # **Detalhamento do Escopo**

**3.1 Funcionalidades por Módulo**

O sistema Optio é composto pelos seguintes módulos:

**Módulo 1 — Interface Web** Responsável pela interação direta com o usuário. Compreende as seguintes funcionalidades:

* Formulário de busca com entrada por palavras-chave e seleção de área de conhecimento;  
* Filtro por modalidade (presencial ou EAD) e por estado ou região;  
* Marcação de cursos como favoritos, com armazenamento no perfil do usuário;  
* Painel de histórico de buscas realizadas;  
* Painel de notificações de novos cursos aderentes ao perfil do usuário.

**Módulo 2 — Autenticação e Cadastro de Usuários** Responsável pelo gerenciamento de identidade e acesso. Compreende:

* Cadastro de novos usuários com e-mail e senha;  
* Autenticação segura;  
* Armazenamento de preferências, favoritos e histórico vinculados ao perfil do usuário.

**Módulo 3 — API Backend** Camada responsável pela orquestração das operações do sistema. Compreende:

* Recebimento e validação das requisições de busca;  
* Confirmação do recebimento da solicitação ao usuário em até 4 segundos;  
* Comunicação com o módulo de coleta de dados e com o serviço de filas;  
* Envio dos resultados consolidados ao usuário no canal de sua preferência (e-mail ou notificação no aplicativo), configurável no perfil.

**Módulo 4 — Coleta e Processamento de Dados** Responsável pela obtenção e estruturação das informações sobre cursos de pós-graduação gratuitos. Utiliza um pipeline estruturado em três etapas:

* **Coleta:** realizada via **Firecrawl**, ferramenta consolidada de mercado que converte páginas web (incluindo páginas renderizadas com JavaScript) em conteúdo estruturado (markdown/JSON), eliminando a complexidade de gerenciar drivers de navegador. Fontes oficiais como Sucupira/CAPES são priorizadas como origem primária;
* **Estruturação:** o conteúdo coletado pelo Firecrawl é processado por um **LLM** (OpenAI ou Google Gemini), que extrai e normaliza os campos relevantes (nome do curso, instituição, modalidade, área, estado, link oficial). O LLM atua exclusivamente como parser do conteúdo coletado — nunca como fonte primária de informação, eliminando o risco de alucinação de dados factuais;
* **Verificação:** todo registro exposto ao usuário deve conter a URL de origem e a data de coleta. Registros sem link verificável para o site oficial do curso não são exibidos. Uma camada de abstração sobre os provedores de LLM será implementada desde o início, permitindo a troca de modelo sem impacto na lógica de negócio (ver R07).

**Módulo 5 — Fila de Processamento Assíncrono** Responsável por garantir a escalabilidade e o desempenho do sistema. Compreende:

* Gerenciamento da fila de solicitações de busca via RabbitMQ;  
* Processamento assíncrono das requisições, desacoplando a confirmação imediata ao usuário da entrega final dos resultados.

**Módulo 6 — Alertas Salvos** Responsável por notificar o usuário proativamente quando novos cursos corresponderem a critérios previamente definidos por ele. Compreende:

* Salvamento de buscas como alertas ativos (por palavras-chave, área, modalidade ou estado);
* Verificação periódica de novos cursos aderentes aos alertas cadastrados;
* Envio de notificação ao usuário no canal de sua preferência quando houver correspondência.

> **Nota:** Esta abordagem substitui a recomendação baseada em histórico — que exigiria volume significativo de dados de uso para ser efetiva — por alertas explícitos configurados pelo próprio usuário, entregando valor imediato desde a v1 sem dependência de dados históricos.

  ---

**3.2 Escopo Negativo**

Os itens a seguir estão explicitamente fora do escopo desta versão do Optio:

* **Cursos pagos:** o sistema indexará exclusivamente cursos de pós-graduação gratuitos;  
* **Integração com sistemas de inscrição:** o Optio não realizará inscrições em nome do usuário nem se integrará a portais de candidatura das instituições;  
* **Aplicativo mobile:** o produto será entregue exclusivamente na modalidade web;  
* **Suporte a outros idiomas:** a plataforma será desenvolvida integralmente em português brasileiro.  
  ---

**3.3 Características de Inovação e Justificativa**

Embora existam iniciativas de catalogação de cursos de pós-graduação — como a Plataforma Sucupira/CAPES (base oficial do governo com todos os programas stricto sensu do país) e o e-MEC — e plataformas comerciais como o Quero Educação, nenhuma dessas soluções atende plenamente ao problema identificado. A Sucupira é uma base completa, mas de navegação burocrática e hostil ao usuário não especializado; o e-MEC é focado em credenciamento institucional; o Quero Educação é orientado a cursos pagos e opera por parcerias comerciais com instituições de ensino, o que limita a abrangência e a imparcialidade dos resultados apresentados.

O Optio se posiciona na intersecção dessas lacunas: utiliza fontes oficiais (como Sucupira/CAPES) como fonte primária confiável e as complementa com coleta automatizada via Firecrawl e processamento por LLM, entregando uma experiência de busca amigável, personalizada e assíncrona — com resultados enviados ao canal de preferência do usuário.

O Optio se diferencia por três aspectos centrais:

1. **Foco exclusivo em gratuidade:** o sistema é dedicado inteiramente a cursos de pós-graduação sem custo para o usuário, um segmento sistematicamente subrepresentado nas plataformas existentes;  
2. **Abordagem de coleta estruturada e confiável:** ao combinar fontes oficiais (Sucupira/CAPES), coleta automatizada via Firecrawl e estruturação por LLM, o Optio não depende de parcerias com instituições para indexar seus cursos, ampliando a cobertura e reduzindo vieses comerciais nos resultados;  
3. **Entrega personalizada e assíncrona:** os resultados são filtrados de acordo com o perfil do usuário e entregues no canal de sua preferência (e-mail, notificação no aplicativo ou outros), sem exigir que o usuário permaneça navegando na plataforma durante o processamento da busca.

5. # **Processo de Desenvolvimento** 

**5.1 Metodologia**

O desenvolvimento do Optio será conduzido com base no framework **Scrum**, complementado por práticas de engenharia de software contínua — como integração contínua e controle de versão — necessárias para sustentar a complexidade técnica do projeto e atender às exigências documentais estabelecidas.

A adoção isolada de um framework ágil, por si só, não é suficiente para cobrir a natureza híbrida do Optio, que envolve componentes de alto risco técnico, decisões arquiteturais ainda em maturação e entregas com critérios formais de aceite. Por isso, o processo foi desenhado para equilibrar a agilidade iterativa do Scrum com o rigor documental exigido pelo contexto do projeto.

---

**5.2 Estrutura das Sprints**

Cada Sprint terá duração de **3 semanas**. O ciclo de cada Sprint contempla as seguintes etapas:

* **Sprint Planning:** definição dos itens do backlog a serem desenvolvidos na Sprint, com estimativa de esforço e critérios de aceite;  
* **Daily Standup:** alinhamento diário do time sobre progresso, impedimentos e próximos passos;  
* **Sprint Review:** apresentação dos incrementos entregues ao gestor ao final de cada Sprint;  
* **Retrospectiva:** avaliação do processo pela equipe, com identificação de pontos de melhoria para a Sprint seguinte.

A verificação e validação das tecnologias de coleta de dados — LLMs e web scraping — serão realizadas **dentro das Sprints**, de forma iterativa, conforme o desenvolvimento avança e os desafios técnicos se apresentam. Essa decisão reflete a natureza dinâmica e mutável do projeto, no qual ajustes de rota são esperados e previstos.

---

**5.3 Artefatos**

Os seguintes artefatos serão mantidos e atualizados ao longo do projeto:

* **Product Backlog:** lista priorizada de funcionalidades e requisitos do sistema, gerenciada no **Jira**;  
* **Sprint Backlog:** subconjunto do Product Backlog selecionado para cada Sprint;  
* **Definition of Done (DoD):** critérios mínimos que um item deve satisfazer para ser considerado concluído, acordados pelo time antes do início do desenvolvimento;  
* **Burndown Chart:** acompanhamento do progresso da Sprint em relação ao esforço planejado, gerado e monitorado via Jira.

---

**5.4 Organização do Time**

O time é composto por **3 a 4 membros**, todos com formação equivalente e capacidade de atuar tanto no desenvolvimento quanto na gestão do projeto. Não há separação formal de papéis técnicos — os membros atuam de forma full stack, assumindo responsabilidades conforme a demanda de cada Sprint. A liderança do projeto é exercida pelo membro com maior perfil de gestão, de forma orgânica e não hierárquica.

Dado o porte e a organização do time, os papéis de **Product Owner** e **Scrum Master** serão exercidos de maneira informal e distribuída, sem atribuição exclusiva a um único membro. 

6. # **Restrições**

**6.1 Restrições de Prazo e Orçamento**

O projeto deve ser concluído até **junho de 2026**, dentro do orçamento estabelecido. Custos variáveis associados ao uso de APIs de LLMs e serviços de infraestrutura em nuvem devem ser monitorados continuamente, dado seu potencial de impacto direto no orçamento disponível.

---

**6.2 Restrições Legais e Regulatórias**

O sistema deve estar em conformidade com as seguintes legislações e regulamentações:

* **Lei Geral de Proteção de Dados (LGPD — Lei nº 13.709/2018):** o Optio coleta e armazena dados pessoais de usuários cadastrados, estando sujeito às obrigações de consentimento, transparência, segurança da informação e direito à exclusão de dados. O sistema deve implementar criptografia, controle de acesso e mecanismos para exclusão segura de registros;  
* **Marco Civil da Internet (Lei nº 12.965/2014):** o sistema deve observar os princípios de privacidade, neutralidade e responsabilidade no tratamento de dados e registros de acesso;  
* **Termos de uso de sites-alvo do scraping:** a coleta de dados por web scraping deve considerar os termos de uso dos sites acessados. O time deverá avaliar, caso a caso, a legalidade e os limites da extração automatizada de dados de cada fonte, mitigando riscos de bloqueio ou penalidades.

---

**6.3 Restrições de Integração com Sistemas Externos**

O Optio depende dos seguintes serviços e sistemas externos para seu funcionamento:

* **APIs de modelos de linguagem (LLMs):** integração com provedores como OpenAI e Google, sujeita a limites de requisições, políticas de uso e custos variáveis por consumo;  
* **Serviço de envio de e-mail:** integração com um provedor de e-mail transacional (como SendGrid ou Amazon SES) para entrega assíncrona dos resultados ao usuário;  
* **RabbitMQ:** utilizado para gerenciamento da fila de processamento assíncrono. Será adotado preferencialmente como serviço gerenciado em nuvem, desde que exista opção gratuita viável (como CloudAMQP). Na ausência de uma opção gratuita adequada, será auto-hospedado;  
* **Selenium:** utilizado para extração de dados via web scraping em fontes que não disponibilizam APIs públicas.

---

**6.4 Limitações e Dependências de Acesso a Dados de Terceiros**

A qualidade e a abrangência dos resultados entregues ao usuário estão diretamente condicionadas a fatores externos ao controle do time:

* **Bloqueio de acesso por sites-alvo:** sites podem implementar mecanismos anti-scraping, limitando ou impedindo a coleta automatizada de dados. O sistema deve prever estratégias de contingência para esse cenário;  
* **Limites e custos das APIs de LLMs:** os provedores de modelos de linguagem impõem cotas de requisições e cobranças variáveis por uso, o que pode impactar tanto o desempenho quanto o orçamento do projeto;  
* **Qualidade dos dados de terceiros:** a precisão e a completude das informações sobre cursos dependem da qualidade e da atualização dos dados disponíveis nas fontes consultadas, não sendo possível garantir a uniformidade dos resultados em todas as situações.

---

**6.5 Restrições de Hardware e Compatibilidade**

O sistema será otimizado para acesso via navegadores web em computadores e tablets em modo paisagem. A responsividade completa para smartphones não será implementada na versão inicial devido a restrições de prazo e recursos da equipe — reconhecida como dívida técnica crítica, dado que mais de 70% do tráfego web no Brasil é originado de dispositivos móveis. A implementação de interface responsiva para smartphones está prevista como prioridade para a v2.

---

**6.6 Restrições de Usabilidade e Acessibilidade**

A interface deve ser intuitiva e de fácil utilização, com suporte a navegação via teclado e mouse e possibilidade de ajuste de tamanho de fonte. Requisitos avançados de acessibilidade, como suporte a leitores de tela, não fazem parte do escopo da versão inicial.

---

**6.7 Restrições de Idioma e Abrangência Geográfica**

A plataforma será desenvolvida integralmente em **português brasileiro**. Não há suporte previsto a outros idiomas na versão inicial. O sistema é voltado ao mercado brasileiro, sem requisitos de compatibilidade com outros fusos horários ou localidades.

7. # **Premissas** 

As premissas a seguir representam as pré-condições assumidas como verdadeiras para que o projeto seja executado conforme planejado. Caso qualquer uma delas não se confirme, o impacto correspondente deverá ser avaliado e tratado como risco ou impedimento.

---

**7.1 Alocação da Equipe**

Assume-se que cada membro da equipe estará disponível para dedicar **no mínimo 10 horas semanais** ao projeto, sendo aproximadamente **2 horas semanais** reservadas para estudo, capacitação e nivelamento técnico nas tecnologias envolvidas. A continuidade do projeto depende da manutenção dessa disponibilidade mínima ao longo de todas as Sprints.

---

**7.2 Infraestrutura e Ambiente de Desenvolvimento**

Assume-se que, no início do projeto, todos os membros da equipe disporão de:

* Máquina própria com ambiente de desenvolvimento local configurado;  
* Acesso à internet de alta velocidade, condição indispensável para o desenvolvimento, testes de scraping e consumo de APIs externas;  
* Acesso ativo ao **Jira** para gestão do backlog e acompanhamento das Sprints.

---

**7.3 Acesso a Serviços Externos**

Assume-se que as contas e credenciais de acesso aos serviços externos necessários serão obtidas **antes do início da Sprint em que cada serviço for utilizado**. São eles:

* **APIs de LLMs** (ex: OpenAI, Google Gemini): ainda não contratadas — a solicitação ou contratação deve ocorrer antes da Sprint que envolva o módulo de coleta de dados;  
* **Serviço de envio de e-mail** (ex: SendGrid, Amazon SES): conta a ser criada antes da implementação do módulo de notificação;  
* **RabbitMQ:** a ser configurado como serviço gerenciado em nuvem, se houver opção gratuita viável, ou auto-hospedado como alternativa.

O projeto assume ainda que os serviços externos contratados manterão disponibilidade e estabilidade suficientes para não comprometer o cronograma de desenvolvimento.

---

**7.4 Competências Técnicas**

Assume-se que o time possui conhecimento prévio em **desenvolvimento web** e **integração com APIs REST**, competências consideradas base para o projeto. Tecnologias como **RabbitMQ** e aspectos avançados de **web scraping com Selenium** serão estudadas e desenvolvidas durante o próprio projeto, dentro da carga semanal prevista para capacitação.

A ausência de domínio prévio nessas tecnologias é um fator de risco conhecido e deve ser considerado no planejamento das Sprints que envolvam esses componentes, com margem de tempo adequada para curva de aprendizado.

---

**7.5 Acesso a Dados de Terceiros**

Assume-se que as fontes de dados consultadas pelo sistema — sites de instituições de ensino e provedores de LLMs — estarão acessíveis durante o desenvolvimento e a operação do sistema. Restrições de acesso, bloqueios de scraping ou mudanças nas políticas de uso de APIs externas não estão sob controle do time e devem ser tratadas como riscos do projeto.

8. # **Riscos** 

A tabela a seguir apresenta os riscos identificados para o projeto Optio, com sua classificação, probabilidade, impacto, e as ações de mitigação e contingência correspondentes.

| \# | Descrição | Categoria | Probabilidade | Impacto | Mitigação | Contingência |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| R01 | Sites-alvo implementarem bloqueios anti-scraping, impedindo a coleta automatizada de dados | Técnico | Altamente Provável | Alto | Diversificar as fontes de coleta; implementar rotação de agentes e delays entre requisições; priorizar fontes com APIs públicas | Substituir a fonte bloqueada por coleta via LLM ou fonte alternativa; registrar a limitação e notificar o time |
| R02 | APIs de LLMs apresentarem custos acima do orçamento previsto | Projeto | Provável | Alto | Monitorar consumo de tokens por Sprint; estabelecer limite de gasto mensal; avaliar modelos mais econômicos durante os testes | Reduzir o uso de LLMs priorizando scraping; migrar para modelo gratuito ou de menor custo; revisar orçamento com o gestor |
| R03 | Contratação das APIs de LLMs atrasar, bloqueando a Sprint correspondente | Projeto | Moderado | Alto | Antecipar a solicitação de acesso antes da Sprint que depende do módulo de coleta; incluir essa ação como item do backlog inicial | Reordenar o backlog para desenvolver módulos independentes enquanto o acesso não é obtido |
| R04 | Curva de aprendizado em RabbitMQ e Selenium impactar o cronograma | Técnico | Provável | Médio | Reservar as 2h semanais de capacitação desde a primeira Sprint; iniciar o estudo dessas tecnologias antes da Sprint que as exige | Simplificar a implementação inicial; buscar apoio externo ou material de referência; renegociar escopo da Sprint afetada |
| R05 | Baixa disponibilidade da equipe (menos de 10h semanais) comprometer entregas | Projeto | Provável | Alto | Alinhar expectativas de disponibilidade com todos os membros antes do início; planejar Sprints com escopo compatível com a carga disponível | Reduzir o escopo da Sprint afetada; redistribuir tarefas entre membros disponíveis; comunicar impacto ao gestor |
| R06 | Qualidade e precisão dos resultados retornados ficarem abaixo dos 80% definidos como meta | Técnico | Moderado | Alto | Realizar testes de relevância desde as primeiras Sprints; refinar prompts e estratégias de coleta iterativamente | Revisar a estratégia de coleta predominante; combinar LLM e scraping para aumentar cobertura e precisão |
| R07 | Provedores de LLM alterarem políticas de uso ou descontinuarem modelos utilizados | Técnico | Improvável | Alto | Não criar dependência exclusiva de um único provedor; abstrair a camada de integração para facilitar troca de modelo | Migrar para provedor alternativo; ajustar prompts ao novo modelo; avaliar impacto no desempenho e nos custos |
| R08 | Não conformidade com os termos de uso de sites-alvo do scraping gerar impedimentos legais | Técnico / Legal | Moderado | Alto | Analisar os termos de uso de cada fonte antes de incluí-la no sistema; priorizar fontes com dados públicos e sem restrição explícita | Remover a fonte infratora do sistema; substituir por coleta via LLM ou fonte alternativa permitida |
| R09 | Falha no serviço de envio de e-mail impactar a entrega dos resultados ao usuário | Técnico | Improvável | Médio | Escolher provedor com SLA confiável; implementar mecanismo de reenvio automático em caso de falha | Notificar o usuário via interface web sobre a indisponibilidade temporária; reprocessar a fila de envios assim que o serviço for restabelecido |
| R10 | Escopo crescer de forma não controlada durante o desenvolvimento | Projeto | Moderado | Médio | Manter o escopo negativo documentado e visível; avaliar toda nova demanda antes de incluir no backlog; exigir aprovação formal para mudanças de escopo | Congelar o escopo da versão atual; mover itens novos para backlog de versões futuras; comunicar impacto ao gestor |

9. # **Estimativa de Tamanho**

**9.1 Contagem NESMA Indicativa**

A contagem NESMA indicativa é uma estimativa preliminar baseada exclusivamente nos Arquivos Lógicos Internos (ALIs) e Arquivos de Interface Externa (AIEs) identificados, aplicando um fator fixo de complexidade.

| Tipo | Quantidade | Fator NESMA | Pontos de Função |
| ----- | ----- | ----- | ----- |
| ALI | 6 | 35 | 210 |
| AIE | 1 | 15 | 15 |
| **Total NESMA Indicativo** |  |  | **225 PF** |

Os ALIs identificados são: Usuários, Histórico de Buscas, Cursos Favoritos, Resultados de Buscas, Configurações de Notificação e Alertas Salvos. O AIE identificado é: Informações de Instituições de Ensino (dados obtidos via Firecrawl e estruturados por LLM).

> **Nota metodológica:** A contagem NESMA indicativa (225 PF) e a contagem IFPUG detalhada (99 PF) apresentam diferença de aproximadamente 2,3x. Isso é esperado: o método NESMA indicativo aplica fatores fixos de complexidade apenas sobre os arquivos lógicos, tendendo a superestimar. A contagem IFPUG, por detalhar individualmente cada função transacional (EEs, CEs e SEs) com sua complexidade real, é mais precisa e deve ser adotada como referência para estimativa de custo e cronograma.

---

**9.2 Contagem IFPUG**

A contagem IFPUG detalha cada função do sistema com sua complexidade e peso correspondente, seguindo o método Function Point Analysis (FPA) versão 4.3.

---

**9.2.1 Arquivos Lógicos Internos (ALIs)**

ALIs são grupos de dados logicamente relacionados mantidos e gerenciados internamente pelo sistema.

| \# | ALI | Descrição | Complexidade | PF |
| ----- | ----- | ----- | ----- | ----- |
| ALI-01 | Usuários | Armazena dados de cadastro, credenciais de autenticação e preferências do usuário | Média | 10 |
| ALI-02 | Histórico de Buscas | Registra as buscas realizadas por cada usuário, incluindo termos, filtros e data | Baixa | 7 |
| ALI-03 | Cursos Favoritos | Armazena os cursos marcados como favoritos vinculados ao perfil do usuário | Baixa | 7 |
| ALI-04 | Resultados de Buscas | Armazena os resultados retornados pelas buscas para consulta e reenvio | Média | 10 |
| ALI-05 | Configurações de Notificação | Armazena as preferências de notificação de cada usuário | Baixa | 7 |
| ALI-06 | Alertas Salvos | Armazena os alertas de busca configurados pelo usuário (critérios, canal de entrega e status ativo/inativo) | Baixa | 7 |
|  |  |  | **Subtotal** | **48** |

---

**9.2.2 Arquivos de Interface Externa (AIEs)**

AIEs são grupos de dados mantidos por sistemas externos, consumidos pelo Optio sem que sejam gerenciados internamente.

| \# | AIE | Descrição | Complexidade | PF |
| ----- | ----- | ----- | ----- | ----- |
| AIE-01 | Informações de Instituições de Ensino | Dados sobre cursos de pós-graduação gratuitos obtidos de fontes externas via LLM e/ou web scraping | Média | 7 |
|  |  |  | **Subtotal** | **7** |

---

**9.2.3 Entradas Externas (EEs)**

EEs são processos que recebem dados do usuário e alteram o estado interno do sistema.

| \# | Entrada | Descrição | ALIs Referenciados | Complexidade | PF |
| ----- | ----- | ----- | ----- | ----- | ----- |
| EE-01 | Cadastro de Usuário | Recebe dados de novo usuário e cria registro no sistema | ALI-01 | Baixa | 3 |
| EE-02 | Login / Autenticação | Recebe credenciais e autentica o usuário na plataforma | ALI-01 | Baixa | 3 |
| EE-03 | Solicitação de Busca | Recebe palavras-chave e filtros (área, modalidade, estado) e dispara o processamento assíncrono | ALI-02, ALI-04 | Média | 4 |
| EE-04 | Marcar / Desmarcar Favorito | Recebe a indicação do usuário e atualiza a lista de cursos favoritos | ALI-03 | Baixa | 3 |
| EE-05 | Criar / Remover Alerta | Recebe os critérios definidos pelo usuário e salva ou remove um alerta de busca ativo | ALI-06 | Baixa | 3 |
|  |  |  |  | **Subtotal** | **16** |

---

**9.2.4 Consultas Externas (CEs)**

CEs são processos que recuperam e apresentam dados ao usuário sem alterá-los.

| \# | Consulta | Descrição | ALIs/AIEs Referenciados | Complexidade | PF |
| ----- | ----- | ----- | ----- | ----- | ----- |
| CE-01 | Consulta ao Perfil do Usuário | Recupera e exibe os dados cadastrais e preferências do usuário | ALI-01 | Baixa | 3 |
| CE-02 | Consulta aos Cursos Favoritos | Recupera e exibe a lista de cursos marcados como favoritos pelo usuário | ALI-03, AIE-01 | Baixa | 3 |
| CE-03 | Consulta às Configurações de Notificação | Recupera e exibe as preferências de notificação do usuário | ALI-05 | Baixa | 3 |
|  |  |  |  | **Subtotal** | **9** |

---

**9.2.5 Saídas Externas (SEs)**

SEs são processos que geram e entregam dados ao usuário, envolvendo lógica de processamento adicional.

| \# | Saída | Descrição | ALIs/AIEs Referenciados | Complexidade | PF |
| ----- | ----- | ----- | ----- | ----- | ----- |
| SE-01 | Confirmação de Recebimento da Busca | Gera e exibe mensagem de confirmação ao usuário em até 4 segundos após a solicitação | ALI-02 | Baixa | 4 |
| SE-02 | Exibição dos Resultados na Interface | Apresenta os resultados consolidados da busca na interface web do usuário | ALI-04, AIE-01 | Média | 5 |
| SE-03 | Envio dos Resultados por Canal Preferido | Gera e envia os resultados da busca ao usuário no canal de sua preferência (e-mail ou notificação no aplicativo) | ALI-04, ALI-05, AIE-01 | Média | 5 |
| SE-04 | Notificação de Novo Curso via Alerta | Verifica periodicamente novos cursos aderentes aos alertas salvos e notifica o usuário no canal configurado | ALI-06, AIE-01 | Média | 5 |
|  |  |  |  | **Subtotal** | **19** |

---

**9.2.6 Resumo da Contagem IFPUG**

| Tipo | Quantidade | Pontos de Função |
| ----- | ----- | ----- |
| Arquivos Lógicos Internos (ALIs) | 6 | 48 |
| Arquivos de Interface Externa (AIEs) | 1 | 7 |
| Entradas Externas (EEs) | 5 | 16 |
| Consultas Externas (CEs) | 3 | 9 |
| Saídas Externas (SEs) | 4 | 19 |
| **Total IFPUG** | **19 funções** | **99 PF** |

10. # **Cronograma**  

O desenvolvimento do Optio está organizado em **3 Sprints de 3 semanas** cada, com previsão de entrega até **junho de 2026**. A distribuição das funcionalidades prioriza, na Sprint 1, o fluxo de maior valor para o usuário — a busca e a entrega de resultados por e-mail — evoluindo nas Sprints seguintes para refinamento, experiência do usuário, recomendação automática e estabilização.

| Funcionalidades | Sprint 1 | Sprint 2 | Sprint 3 |
| ----- | :---: | :---: | :---: |
| cadastro e autenticação de usuários | x |  |  |
| Formulário de busca com palavras chaves e filtros básicos | x |  |  |
| Integração Inicial com LLM e/ou WebScrapping | x |  |  |
| Fila de processamento assíncrono | x |  |  |
| Confirmação de recebimento da busca em até 4 segundos | x |  |  |
| Envio dos resultados por e-mail | x |  |  |
| Refinamento de prompts e estratégia de coleta híbrida |  | x |  |
| Validação de precisão de resultados (meta \>= 80%) |  | x |  |
| Cobertura nacional (EAD e presencial) |  | x |  |
| Filtro por modalidade (presencial ou EAD) |  | x |  |
| Filtro por estado ou região |  | x |  |
| Histórico de buscas  |  |  | x |
| Cursos Favoritos |  |  | x |
| Consulta ao perfil do usuário |  |  | x |
| Configurações de notificação |  |  | x |
| Testes de carga e desempenho |  |  | x |
| Ajuste de segurança e conformidade LGPD |  |  | x |
| Correção de bugs e refinamentos finais |  |  | x |
| Documentação técnica final |  |  | x |

11. # **Equipe**

A equipe proposta para o desenvolvimento deste projeto é a seguinte:

| Nome | Função | Horas/Mês | Número de Meses |
| :---: | :---: | :---: | :---: |
| Janderson Lima Dos Santos | Product Owner | | |
| Joana Elise Araujo Lopes | Desenvolvedora | | |
| Maria Eduarda de Almeida Vitorino | Desenvolvedora | | |

12. # **Orçamento** 
**12.1 Custo de Desenvolvimento**

Considerando o escopo apurado de **99 Pontos de Função (PF)**, conforme detalhado na contagem IFPUG apresentada na Seção 9, e o custo unitário de **R$ 600,00 (seiscentos reais) por Ponto de Função**, o valor estimado para o desenvolvimento do projeto é de:

**R$ 59.400,00 (cinquenta e nove mil e quatrocentos reais)**

---

**12.2 Custo de Consumo de APIs Externas (Firecrawl + LLM)**

O pipeline de coleta do Optio envolve dois serviços externos cobrados por uso: o **Firecrawl** (responsável pela coleta e conversão de páginas web) e uma **API de LLM** (responsável pela estruturação do conteúdo coletado). Os custos foram estimados com três cenários — otimista, realista e pessimista — para refletir a incerteza sobre o volume de uso e a complexidade das páginas processadas.

**Premissas do pipeline por busca:**

* O Firecrawl coleta N páginas por busca e as converte em markdown estruturado (1 crédito/página);
* O LLM processa cada página individualmente para extrair os campos relevantes do curso;
* Estimativa de **5.000 tokens de entrada e 400 tokens de saída por página** processada pelo LLM;
* Cotação do dólar adotada: **R$ 5,80** (valor conservador);
* Período considerado: **6 meses** (janeiro a junho de 2026).

**Modelos de LLM de referência por cenário:**

| Cenário | Modelo | Input /1M tokens | Output /1M tokens |
| ----- | ----- | ----- | ----- |
| Otimista | Gemini 2.5 Flash-Lite | US$ 0,10 | US$ 0,40 |
| Realista | GPT-4o-mini | US$ 0,15 | US$ 0,60 |
| Pessimista | GPT-4o | US$ 2,50 | US$ 10,00 |

> A escolha definitiva do modelo ocorrerá durante as Sprints, com base em testes de precisão e custo. A camada de abstração de LLM (ver Módulo 4) permite troca de modelo sem impacto na lógica de negócio.

**Estimativa por cenário (6 meses):**

| Componente | Otimista | Realista | Pessimista |
| ----- | ----- | ----- | ----- |
| Volume (buscas/mês) | 100 | 300 | 1.000 |
| Páginas coletadas por busca | 5 | 8 | 15 |
| Plano Firecrawl | Hobby (US$ 16/mês) | Hobby (US$ 16/mês) | Standard (US$ 83/mês) |
| Tokens de entrada por busca | ~25.000 | ~40.000 | ~150.000 |
| Tokens de saída por busca | ~2.000 | ~3.200 | ~6.000 |
| Custo LLM por busca | US$ 0,003 | US$ 0,008 | US$ 0,435 |
| Custo LLM mensal | US$ 0,33 | US$ 2,40 | US$ 435,00 |
| Custo Firecrawl mensal | US$ 16,00 | US$ 16,00 | US$ 83,00 |
| **Total mensal (USD)** | **US$ 16,33** | **US$ 18,40** | **US$ 518,00** |
| **Total mensal (BRL)** | **R$ 94,71** | **R$ 106,72** | **R$ 3.004,40** |
| **Total 6 meses (BRL)** | **R$ 568,26** | **R$ 640,32** | **R$ 18.026,40** |

O orçamento do projeto adota o **cenário realista** como base (R$ 640,32 em 6 meses). Caso o volume de buscas supere 500/mês de forma sustentada, o custo mensal deverá ser reavaliado — o cenário pessimista representa um gatilho de revisão orçamentária a ser monitorado a partir da Sprint 2.

---

**12.3 Margem de Contingência para Infraestrutura em Nuvem**

Para cobrir custos variáveis de infraestrutura — incluindo hospedagem da aplicação, serviço de envio de e-mail transacional e eventuais variações de consumo não previstas —, aplica-se uma **margem de contingência de 20%** sobre o custo total do projeto.

| Item | Valor |
| ----- | ----- |
| Custo de desenvolvimento (PF) | R$ 59.400,00 |
| Custo estimado de APIs externas — cenário realista (6 meses) | R$ 640,32 |
| **Subtotal** | **R$ 60.040,32** |
| Margem de contingência (20%) | R$ 12.008,06 |
| **Total Geral Estimado** | **R$ 72.048,38** |

---

**Resumo Executivo de Custos**

| Componente | Valor |
| ----- | ----- |
| Desenvolvimento (99 PF × R$ 600,00) | R$ 59.400,00 |
| APIs externas — Firecrawl + LLM (cenário realista, 6 meses) | R$ 640,32 |
| Contingência de infraestrutura (20%) | R$ 12.008,06 |
| **Total Estimado do Projeto** | **R$ 72.048,38** |

