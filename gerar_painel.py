#!/usr/bin/env python3
"""
Gerador do Painel de Normativos do DOU.

Consulta o endpoint público de busca do Diário Oficial da União
(in.gov.br) para os temas de interesse e monta uma página HTML
autocontida (index.html) no mesmo layout do painel publicado neste
repositório.

Na versão originalmente usada por Darci de Borba, a busca e a curadoria
eram feitas por um assistente de IA (Claude, via Cowork) — ver
PROMPT.md. Este script automatiza a parte reprodutível (consulta e
template); a classificação temática fina e o resumo da ementa em uma
frase seguem sendo revisados por IA ou por um humano.

Uso:
    python gerar_painel.py
"""

from __future__ import annotations

import datetime as dt
import html
import json
import urllib.parse
import urllib.request

TEMAS: dict[str, str] = {
    "Governo Digital": "governo digital",
    "Inteligência Artificial": "inteligência artificial",
    "Processos Administrativos": "processo administrativo",
    "Pesquisa Acadêmica": "pesquisa científica",
    "Administração Pública": "administração pública",
}

ITENS_POR_TEMA = 6
BUSCA_URL = "https://www.in.gov.br/consulta/-/buscar/dou"


def buscar_normativos(termo: str, limite: int = ITENS_POR_TEMA) -> list[dict]:
    """Consulta a busca pública do DOU e retorna os itens mais recentes para o termo."""
    params = {
        "q": termo,
        "exactDate": "personalizado",
        "sortType": "0",  # mais recentes primeiro
    }
    url = f"{BUSCA_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "painel-normativos-dou/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        itens = data.get("items") or data.get("result", {}).get("items", [])
        return itens[:limite]
    except Exception as exc:
        print(f"[aviso] falha ao consultar DOU para '{termo}': {exc}")
        return []


def render_card(item: dict) -> str:
    titulo = html.escape(item.get("title") or item.get("titulo") or "Sem título")
    ementa = html.escape((item.get("content") or item.get("ementa") or "")[:220])
    secao = html.escape(str(item.get("pubName") or item.get("secao") or ""))
    data_pub = html.escape(str(item.get("pubDate") or item.get("data") or ""))
    link = html.escape(item.get("urlTitle") and f"https://www.in.gov.br{item['urlTitle']}" or item.get("link") or "#")
    return f"""
      <a class="card" href="{link}" target="_blank" rel="noopener">
        <div class="card-title">{titulo}</div>
        <div class="card-meta">{secao} — {data_pub}</div>
        <div class="card-summary">{ementa}</div>
      </a>"""


def render_secao(tema: str, itens: list[dict]) -> str:
    cards = "\n".join(render_card(i) for i in itens) or "<p class='muted'>Nenhum normativo encontrado nesta rodada.</p>"
    return f"""
    <section class="theme">
      <div class="theme-header"><h2>{html.escape(tema)}</h2><span class="count">{len(itens)} ato(s)</span></div>
      <div class="grid">{cards}
      </div>
    </section>"""


def montar_html(secoes_html: str, data_geracao: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Painel Diário de Normativos Legais - Diário Oficial da União</title>
<style>
  :root{{--bg:#0f1626; --panel:#161f33; --panel2:#1c2740; --border:#2a3654; --text:#e8ecf5; --muted:#96a2bf; --accent:#5b8def;}}
  *{{box-sizing:border-box;}}
  body{{margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    background:linear-gradient(180deg,#0b1120,#0f1626 400px); color:var(--text); line-height:1.55;}}
  header{{padding:36px 24px 20px; max-width:1100px; margin:0 auto;}}
  header h1{{margin:0 0 6px; font-size:1.7rem; font-weight:700;}}
  header .sub{{color:var(--muted); font-size:0.95rem;}}
  main{{max-width:1100px; margin:0 auto; padding:0 24px 60px;}}
  section.theme{{margin-top:34px;}}
  .theme-header{{display:flex; align-items:baseline; gap:10px; margin-bottom:14px; border-bottom:1px solid var(--border); padding-bottom:8px;}}
  .theme-header h2{{font-size:1.15rem; margin:0; font-weight:650;}}
  .theme-header .count{{color:var(--muted); font-size:0.85rem;}}
  .grid{{display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:16px;}}
  a.card{{display:flex; flex-direction:column; gap:10px; background:var(--panel); border:1px solid var(--border);
    border-radius:12px; padding:18px; text-decoration:none; color:var(--text);}}
  a.card:hover{{border-color:var(--accent); background:var(--panel2);}}
  .card-title{{font-size:1rem; font-weight:650;}}
  .card-meta{{font-size:0.78rem; color:var(--muted);}}
  .card-summary{{font-size:0.86rem; color:#c4cbdf;}}
  .muted{{color:var(--muted);}}
</style>
</head>
<body>
<header>
  <h1>Painel Diário de Normativos Legais</h1>
  <div class="sub">Diário Oficial da União — gerado em {data_geracao}</div>
</header>
<main>{secoes_html}
</main>
</body>
</html>"""


def main() -> None:
    data_geracao = dt.date.today().strftime("%d/%m/%Y")
    secoes = [render_secao(tema, buscar_normativos(termo)) for tema, termo in TEMAS.items()]
    pagina = montar_html("\n".join(secoes), data_geracao)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(pagina)
    print("index.html atualizado.")


if __name__ == "__main__":
    main()
