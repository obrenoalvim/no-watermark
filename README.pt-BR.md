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

`clean` sempre sai com código 0. `detect` sai com código 1 se encontrar algo (útil em scripts/CI).

## O que é removido

| Categoria | Exemplos | Ação |
|---|---|---|
| Caracteres de formatação (Unicode Cf) | espaço/juntor/não-juntor de largura zero, juntor de palavra, BOM, controles bidirecionais | removido |
| Seletores de variação | U+FE00–FE0F, U+E0100–E01EF | removido |
| Bloco de tag | U+E0000–E007F | removido (exceto quando parte de uma sequência de bandeira-emoji) |
| Espaços anômalos | os 16 caracteres de espaço "Zs" do Unicode que não são ASCII (NBSP, marca de espaço Ogham, espaços fino/cabelo/em/en, espaço ideográfico, etc.) | normalizado para espaço comum |
| Variantes de separador de linha | NEL (U+0085), SEPARADOR DE LINHA (U+2028), SEPARADOR DE PARÁGRAFO (U+2029) | normalizado para `\n` |
| Outros | hífen suave, separador de vogal mongol, juntor de grafema combinante | removido |

A cobertura de espaços vem da categoria Unicode "Zs" inteira, não de uma lista escolhida à mão — isso importa porque pesquisa atual de watermarking de LLM (ex: [Innamark, IEEE Access 2025](https://arxiv.org/html/2502.12710)) marca o texto substituindo espaços comuns por *qualquer* caractere Zs visualmente idêntico, então cobertura parcial é fácil de contornar.

## Segurança de emoji

ZWJ/ZWNJ e caracteres do bloco de tag também são usados legitimamente em emoji (sequências de família/casal, sequências de bandeira) e em alguns idiomas (ZWNJ em texto índico). Por padrão, `nowatermark` não remove esses caracteres quando estão ao lado de codepoints de emoji ou dentro de uma sequência válida de bandeira-emoji. Passe `--no-emoji-guard` pra remover incondicionalmente.

## Skill de agente

Veja `skill/SKILL.md` — instale no seu diretório de skills do AI coding agent pra deixar o the AI agent detectar/limpar marcas d'água em texto que você cola ou referencia durante uma conversa.

## Desenvolvimento

```bash
pip install -e ".[dev]"
pytest -v
```
