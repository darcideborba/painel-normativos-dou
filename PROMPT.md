# Prompt / instrução usada para gerar este painel

Assim como o painel de artigos, este painel é produzido em sessão com o Claude (Cowork), que busca, filtra e monta o HTML a partir da instrução abaixo; o script `gerar_painel.py` automatiza a parte de busca e templating usando a API pública de consulta do Diário Oficial da União.

## Instrução (prompt) usada

> Monte um "Painel de Normativos do DOU" em HTML autocontido (visual escuro), reunindo os atos publicados no Diário Oficial da União mais relevantes para os seguintes temas: governo digital, inteligência artificial, processos administrativos, pesquisa acadêmica e administração pública.
>
> Para cada normativo, traga: tipo de ato (decreto, portaria, instrução normativa etc.), órgão emissor, número, data de publicação, ementa/resumo em uma frase, seção do DOU e link direto para a publicação no site do Diário Oficial da União (in.gov.br).
>
> Organize por tema, com um cabeçalho indicando a data (ou período, se for painel semanal) de referência.
>
> Gere a página como um artefato HTML autocontido; ao atualizar, sobrescreva o mesmo artefato em vez de criar um novo.
>
> Gerar apenas sob demanda, sem tarefa agendada.

## Fonte de dados

Consulta pública ao Diário Oficial da União via `in.gov.br` (endpoint de busca usado pelo próprio site). O script incluído aqui automatiza essa consulta; a classificação temática fina e a redação da ementa resumida seguem sendo revisadas por IA/humano.
