# no-watermark

*[Read in English](README.md)*

Detecta e remove marcas d'água de Unicode invisível em texto — caracteres de largura zero, seletores de variação, esteganografia via bloco de tag Unicode, controles bidirecionais e substituição de espaços anômalos. Remoção 100% determinística dentro desse escopo; não mexe em sequências de emoji legítimas por padrão.

**Fora de escopo:** marcas d'água estatísticas de distribuição de token (ex: watermarking estilo Kirchenbauer, listas verde/vermelho). Essas exigem reescrever o texto e não têm garantia de remoção — não são tratadas por essa ferramenta.

## Instalação

```bash
pip install -e .
```

## Uso via CLI

```bash
# escaneia um arquivo em busca de caracteres de marca d'água
nowatermark detect suspeito.txt

# limpa um arquivo, escreve em um novo arquivo, imprime o que foi removido
nowatermark clean suspeito.txt -o limpo.txt --report

# passa texto via pipe
echo "algum texto" | nowatermark clean -
```

Códigos de saída: `0` limpo/sucesso, `1` `detect` achou caractere de watermark, `2` erro de uso/IO (arquivo faltando, UTF-8 inválido, caminho é diretório) — mensagem simples no stderr, sem traceback do Python.

## O que é removido

| Categoria | Exemplos | Ação |
|---|---|---|
| Caracteres de formatação (Unicode Cf) | espaço/juntor/não-juntor de largura zero, juntor de palavra, BOM, controles bidirecionais | removido |
| Seletores de variação | U+FE00–FE0F, U+E0100–E01EF | removido |
| Bloco de tag | U+E0000–E007F | removido (exceto quando parte de uma sequência de bandeira-emoji) |
| Espaços anômalos | os 16 caracteres de espaço "Zs" do Unicode que não são ASCII (NBSP, marca de espaço Ogham, espaços fino/cabelo/em/en, espaço ideográfico, etc.) | normalizado para espaço comum |
| Variantes de separador de linha | NEL (U+0085), SEPARADOR DE LINHA (U+2028), SEPARADOR DE PARÁGRAFO (U+2029) | normalizado para `\n` |
| Área de Uso Privado | U+E000–F8FF (BMP) mais os dois planos suplementares de PUA | removido |
| Outros | hífen suave, separador de vogal mongol, juntor de grafema combinante, filler de compatibilidade Hangul (U+3164) | removido |

A cobertura de espaços vem da categoria Unicode "Zs" inteira, não de uma lista escolhida à mão — isso importa porque pesquisa atual de watermarking de LLM (ex: [Innamark, IEEE Access 2025](https://arxiv.org/html/2502.12710)) marca o texto substituindo espaços comuns por *qualquer* caractere Zs visualmente idêntico, então cobertura parcial é fácil de contornar.

Cruzado com [guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) (13k+ stars, ferramenta open-source líder dessa categoria em agosto de 2026) pra fechar 2 gaps: cobertura de Área de Uso Privado tava faltando por completo, e a checagem de preservação de bandeira-emoji usava um walk pra trás que dava pra enganar preservando também caractere de payload colado logo depois do cancel tag que termina uma sequência de bandeira legítima. Os dois corrigidos nesse ciclo.

## Detecção de homoglyph (heurística, só detecção)

`nowatermark detect` também sinaliza palavras que misturam letras latinas com Cirílico ou Grego visualmente idênticos (ex: `а` cirílico no lugar de `a` latino) — técnica real pra esconder payload sem nenhum caractere invisível, confirmada em uso atual por [pesquisa independente sobre a onda de ferramentas de remoção de watermark de IA de agosto de 2026](https://www.bleepingcomputer.com/news/security/ai-watermark-removers-flood-the-web-almost-none-can-prove-they-work/). Isso é reportado separado e nunca afeta o exit code do `detect` — misturar scripts dentro de uma palavra é raro em texto legítimo mas não impossível, então é sinal pra checar, não achado determinístico. `clean` não mexe nisso (reescrever caractere visível automaticamente é uma garantia diferente, mais arriscada, do que remover invisível — ver `TODO IMPROVEMENTS.md`).

## Segurança de emoji

ZWJ/ZWNJ e caracteres do bloco de tag também são usados legitimamente em emoji (sequências de família/casal, sequências de bandeira) e em alguns idiomas (ZWNJ em texto índico). Por padrão, `nowatermark` não remove esses caracteres quando estão ao lado de codepoints de emoji ou dentro de uma sequência válida de bandeira-emoji. Passe `--no-emoji-guard` pra remover incondicionalmente.

## Skill de agente

`skill/SKILL.md` empacota isso como uma skill instalável para agentes de IA que suportam o formato SKILL.md — coloque no diretório de skills do seu agente pra ele detectar/limpar marcas d'água em texto automaticamente durante uma sessão.

## Desenvolvimento

```bash
pip install -e ".[dev]"
pytest -v
```
