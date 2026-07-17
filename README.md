# CTI News Correlation

## Descrição

O projeto tem como objetivo automatizar a coleta, processamento, correlação e notificação de notícias relacionadas à Segurança da Informação e Cyber Threat Intelligence (CTI).

As notícias são coletadas de diferentes fontes, armazenadas em banco de dados, processadas e enriquecidas para identificar conteúdos relevantes aos ativos monitorados pela organização. O sistema também permite a correlação de informações e a geração de alertas por diferentes canais.

## Funcionalidades

- Coleta automática de notícias via RSS e outras fontes.
- Armazenamento das notícias em PostgreSQL.
- Remoção de notícias duplicadas.
- Correlação de notícias relacionadas.
- Extração de informações relevantes, como:
  - CVEs
  - IOCs
  - Produtos afetados
  - Fabricantes
  - Proof of Concept (PoC)
- Filtragem baseada nos ativos monitorados.
- Geração de alertas por e-mail e outros canais.

## Tecnologias

- Python
- PostgreSQL
- Ollama
- LangChain

## Objetivos

- Automatizar a coleta de inteligência de ameaças.
- Reduzir o volume de análise manual.
- Priorizar notícias relevantes.
- Correlacionar informações provenientes de diferentes fontes.
- Auxiliar equipes de Segurança da Informação na identificação rápida de ameaças.
