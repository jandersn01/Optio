

|  |
| ----- |
| Proposta de Projeto    Optio  |
|  |
| **24/02/2026** |

**Histórico de Revisões**

| Revisão | Data | Autor | Descrição |
| :---: | :---: | :---: | :---: |
|  |  |  |  |
|  |  |  |  |

1. 

**Conteúdo**

[1\.	Sobre o documento	4](#sobre-o-documento)

[2\.	Contexto, descrição do Problema/Motivação	4](#contexto/descrição-do-problema/motivação)

[3\.	Objetivos do Projeto	4](#objetivos-do-projeto)

[4\.	Detalhamento do Escopo	4](#detalhamento-do-escopo)

[5\.	Processo de Desenvolvimento	4](#processo-de-desenvolvimento)

[6\.	Restrições	4](#restrições)

[7\.	Premissas	4](#premissas)

[8\.	Riscos	5](#riscos)

[9\.	Estimativa de Tamanho	5](#estimativa-de-tamanho)

[10\.	Cronograma 	5](#cronograma)

[11\.	Equipe	5](#equipe)

[12\.	Orçamento	5](#orçamento)

1. #  **Sobre o documento** {#sobre-o-documento}

O presente documento constitui a proposta técnica do projeto **Optio**. Estão aqui definidos o escopo, as especificações funcionais e o planejamento para o desenvolvimento de um sistema de pesquisa e agregação de informações sobre cursos de pós-graduação. A finalidade deste documento é descrever o produto de software a ser desenvolvido, suas funcionalidades e os critérios que orientarão sua execução.

2. # **Contexto/Descrição do Problema/Motivação** {#contexto/descrição-do-problema/motivação}

	A decisão sobre a continuidade da formação acadêmica é um momento crítico na trajetória de qualquer profissional. Seja ao término da graduação ou em um momento de transição na carreira, a pergunta sobre qual caminho seguir — e como se qualificar para isso — é recorrente e muitas vezes difícil de responder. A dificuldade, nesse contexto, não está na ausência de informação, mas em sua dispersão: dados sobre cursos de pós-graduação estão fragmentados em múltiplas fontes, sem um ponto centralizado de consulta, o que dificulta a comparação de opções e prejudica uma tomada de decisão fundamentada.

Esse cenário é ainda mais desafiador quando o critério financeiro entra em jogo. Cursos de pós-graduação gratuitos existem em todo o Brasil — oferecidos por instituições públicas, programas governamentais e iniciativas de fomento à educação —, mas localizar essas oportunidades exige do interessado uma pesquisa extensa, dispersa e frequentemente incompleta.

O **Optio** surge como resposta a esse problema. Trata-se de um sistema de pesquisa capaz de reunir e apresentar informações sobre cursos de pós-graduação **gratuitos** oferecidos em todo o Brasil, nas modalidades presencial e EAD, filtrando resultados de acordo com a área de interesse do usuário ou por palavras-chave por ele informadas. A obtenção dessas informações será realizada por meio de uma abordagem híbrida de coleta de dados, cujos detalhes técnicos estão descritos na seção de arquitetura do sistema.

O nome *Optio*, do latim, significa *escolha*, *opção*, *liberdade de decidir* — um posicionamento que reflete diretamente o propósito do produto: oferecer ao usuário o embasamento necessário para que sua decisão sobre o próximo passo acadêmico ou profissional seja segura e bem-informada.

3. # **Objetivos do Projeto** {#objetivos-do-projeto}

**3.1 Objetivo Geral**

Desenvolver o **Optio**, um sistema web que centraliza e entrega, de forma personalizada, informações sobre cursos de pós-graduação gratuitos oferecidos em todo o território nacional, nas modalidades presencial e EAD, reduzindo o esforço e o tempo despendido pelo usuário na pesquisa dessas oportunidades.

---

**3.2 Objetivos Específicos**

Os objetivos específicos do projeto são definidos segundo o critério S.M.A.R.T — isto é, são específicos, mensuráveis, atingíveis, relevantes e temporalmente delimitados.

**a) Confirmação de solicitação em tempo hábil** O sistema deve confirmar o recebimento de cada solicitação de busca em até **4 segundos** após o envio, garantindo ao usuário retorno imediato sobre o processamento da sua requisição, com entrega dos resultados realizada de forma assíncrona via e-mail. Meta a ser atingida até **maio de 2026**.

**b) Relevância dos resultados** Pelo menos **80% dos resultados** retornados pelo sistema devem ser pertinentes à área de interesse ou às palavras-chave informadas pelo usuário, aferidos por meio de testes de validação com usuários ou avaliadores designados. Meta a ser atingida até **maio de 2026**.

**c) Cobertura nacional** O sistema deve ser capaz de indexar e retornar cursos de pós-graduação gratuitos de instituições localizadas em todos os **27 estados** do Brasil, contemplando ambas as modalidades: presencial e EAD. Meta a ser atingida até **maio de 2026**.

**d) Cobertura de resultados por busca** O sistema deve retornar todos os cursos aderentes aos critérios informados pelo usuário, sem limite mínimo imposto — podendo retornar zero resultados quando nenhuma oferta corresponder à pesquisa, comunicando essa ausência de forma clara ao usuário. Meta a ser atingida até **maio de 2026**.

4. # **Detalhamento do Escopo** {#detalhamento-do-escopo}

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
* Envio dos resultados consolidados ao usuário via e-mail.

**Módulo 4 — Coleta e Processamento de Dados** Responsável pela obtenção das informações sobre cursos de pós-graduação gratuitos. Utiliza uma abordagem híbrida, podendo combinar:

* Integração com APIs de modelos de linguagem (LLMs), com desenvolvimento, teste e refinamento de prompts e possível uso de mais de um modelo em conjunto;  
* Extração de dados via web scraping. A definição da estratégia predominante ocorrerá durante a fase de desenvolvimento, com base em testes de precisão e desempenho.

**Módulo 5 — Fila de Processamento Assíncrono** Responsável por garantir a escalabilidade e o desempenho do sistema. Compreende:

* Gerenciamento da fila de solicitações de busca via RabbitMQ;  
* Processamento assíncrono das requisições, desacoplando a confirmação imediata ao usuário da entrega final dos resultados.

**Módulo 6 — Recomendação Automática** Responsável por sugerir cursos proativamente com base no perfil do usuário. Compreende:

* Análise do histórico de buscas e preferências cadastradas;  
* Geração e envio de notificações sobre novos cursos aderentes ao perfil do usuário.  
  ---

**3.2 Escopo Negativo**

Os itens a seguir estão explicitamente fora do escopo desta versão do Optio:

* **Cursos pagos:** o sistema indexará exclusivamente cursos de pós-graduação gratuitos;  
* **Integração com sistemas de inscrição:** o Optio não realizará inscrições em nome do usuário nem se integrará a portais de candidatura das instituições;  
* **Aplicativo mobile:** o produto será entregue exclusivamente na modalidade web;  
* **Suporte a outros idiomas:** a plataforma será desenvolvida integralmente em português brasileiro.  
  ---

**3.3 Características de Inovação e Justificativa**

Embora existam no mercado plataformas agregadoras de cursos — como o Quero Educação —, essas soluções são predominantemente orientadas a cursos pagos e operam mediante parcerias comerciais com instituições de ensino, o que limita a abrangência e a imparcialidade dos resultados apresentados.

O Optio se diferencia por três aspectos centrais:

1. **Foco exclusivo em gratuidade:** o sistema é dedicado inteiramente a cursos de pós-graduação sem custo para o usuário, um segmento sistematicamente subrepresentado nas plataformas existentes;  
2. **Abordagem híbrida de coleta:** ao combinar modelos de linguagem (LLMs) e web scraping, o Optio não depende de parcerias com instituições para indexar seus cursos, o que amplia a cobertura e reduz vieses comerciais nos resultados;  
3. **Entrega personalizada e assíncrona:** os resultados são filtrados de acordo com o perfil do usuário e entregues diretamente por e-mail, sem exigir que o usuário permaneça navegando na plataforma durante o processamento da busca.  
* 

5. # **Processo de Desenvolvimento** {#processo-de-desenvolvimento}

O trabalho será executado com a utilização do Scrum como metodologia ágil, com o desenvolvimento separado por Sprints. Isso possibilitará testes, integração contínua e 

6. # **Restrições** {#restrições}

Algumas possíveis restrições que podem ser aplicadas ao sistema são:

* Restrição de Orçamento: O projeto deve ser concluído dentro de um determinado orçamento e não pode excedê-lo.  
* Restrição de Tempo: O sistema deve ser desenvolvido e implementado dentro de um prazo específico, conforme negociado com o cliente.  
* Restrições de Hardware: O sistema será primariamente otimizado para execução em navegadores web em computadores (notebooks) e tablets em modo paisagem. A versão inicial não será priorizada para smartphones.  
* Restrições de Segurança e Privacidade: O sistema deve atender aos requisitos de segurança, privacidade e proteção de dados do usuário, conforme a Lei Geral de Proteção de Dados (LGPD), incluindo criptografia, auditoria de acesso e mecanismos para exclusão segura de registros.  
* Restrições de Usabilidade: O sistema deve ser fácil de usar e acessível, com suporte a navegação via teclado e mouse, e ajustes de fonte. Não haverá requisitos avançados como leitor de tela na versão inicial.  
* Restrição de Responsividade para Smartphones: A versão inicial do sistema será otimizada para desktop (notebooks) e tablets em modo paisagem. A responsividade completa para smartphones não será priorizada na versão inicial, mas poderá ser incrementada em versões posteriores.  
* Restrições Geográficas: O sistema será inicialmente desenvolvido para atender às necessidades dos terapeutas ocupacionais autônomos e pequenos consultórios no mercado brasileiro. Não há requisitos explícitos para compatibilidade com outros fusos horários ou idiomas além do português na versão inicial.  
* Restrições de Interoperabilidade

7. # **Premissas** {#premissas}

8. # **Riscos** {#riscos}

9. # **Estimativa de Tamanho** {#estimativa-de-tamanho}

10. # **Cronograma**  {#cronograma}

O Prazo de desenvolvimento é detalhado a seguir:

| Funcionalidades | Sprint 1 | Sprint 2 | Sprint 3 |
| ----- | :---: | :---: | :---: |
| Funcionalidade X | x |  |  |
| Funcionalidade Y | x |  |  |
| ... |  | X |  |
| ... |  |  | X |
| ... |  |  |  |

11. # **Equipe** {#equipe}

A equipe proposta para o desenvolvimento deste projeto é a seguinte:

| Nome | Função | Horas/Mês | Número de Meses |
| :---: | :---: | :---: | :---: |
| Janderson Lima Dos Santos |  |  |  |
| Joana Elise Araujo Lopes |  |  |  |
| Felipe Brito |  |  |  |
| Maria Eduarda de Almeida Vitorino |  |  |  |

12. # **Orçamento** {#orçamento}

Considerando o escopo e o custo do ponto de função individual de R$ xxxxx (xxxxx), o valor para a execução do projeto será de R$ xxxxx (xxxxx). 