<div align="center">

<img src=".github/logo.svg" alt="Logo do no-watermark" width="120" height="120">

# no-watermark

**Encontre e remova os caracteres invisíveis escondidos no seu texto.**<br>
Caracteres de largura zero, seletores de variação, esteganografia no bloco de tag, controles bidirecionais e espaços parecidos. Uma CLI em Python e uma skill de agente.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/obrenoalvim/no-watermark?style=flat&logo=github&color=f472b6)](https://github.com/obrenoalvim/no-watermark/stargazers)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)

[English](README.md) · **Português** · [Español](README.es.md)

[Início rápido](#início-rápido) · [Exemplo](#exemplo) · [Uso via CLI](#uso-via-cli) · [O que é removido](#o-que-é-removido) · [Segurança de emoji](#segurança-de-emoji) · [Skill de agente](#skill-de-agente) · [Perguntas frequentes](#perguntas-frequentes)

</div>

---

Detecta e remove marcas d'água de Unicode invisível em texto: caracteres de largura zero, seletores de variação, esteganografia via bloco de tag Unicode, controles bidirecionais e substituição de espaços anômalos. A remoção é 100% determinística dentro desse escopo, e sequências de emoji legítimas ficam intactas por padrão.

Caracteres escondidos podem carregar uma carga que você nunca vê: uma marca d'água de texto, ou uma instrução dirigida a um modelo de IA (conhecida como ASCII smuggling ou prompt injection por caracteres invisíveis). O `nowatermark` mostra o que há no texto e remove.

**Fora de escopo:** marcas d'água estatísticas de distribuição de token (ex: watermarking estilo Kirchenbauer, listas verde/vermelho). Essas exigem reescrever o texto e não têm garantia de remoção, então essa ferramenta não trata delas.

## Início rápido

```bash
pip install git+https://github.com/obrenoalvim/no-watermark.git
nowatermark detect suspeito.txt
```

Precisa de Python 3.10 ou mais novo. Ainda não há release no PyPI.

## Exemplo

Teste no fixture que vem com o repositório (`tests/fixtures/watermarked_sample.txt`):

```console
$ nowatermark detect tests/fixtures/watermarked_sample.txt
U+200B ZERO WIDTH SPACE [format-char] x1
U+200C ZERO WIDTH NON-JOINER [format-char] x1
U+200D ZERO WIDTH JOINER [format-char] x1
U+FEFF ZERO WIDTH NO-BREAK SPACE [format-char] x1
U+3000 IDEOGRAPHIC SPACE [space-variant] x1
U+00AD SOFT HYPHEN [other-invisible] x1
total: 6 watermark character(s) found

$ nowatermark clean tests/fixtures/watermarked_sample.txt -o limpo.txt --report
removed U+200B [format-char] x1
removed U+200C [format-char] x1
removed U+200D [format-char] x1
removed U+FEFF [format-char] x1
removed U+3000 [space-variant] x1
removed U+00AD [other-invisible] x1
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

Códigos de saída: `0` limpo/sucesso, `1` `detect` achou caractere de watermark, `2` erro de uso/IO (arquivo faltando, UTF-8 inválido, caminho é diretório). Os erros saem como mensagem simples no stderr, sem traceback do Python.

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

A cobertura de espaços vem da categoria Unicode "Zs" inteira, não de uma lista escolhida à mão. Isso importa porque pesquisa atual de watermarking de LLM (ex: [Innamark, IEEE Access 2025](https://arxiv.org/html/2502.12710)) marca o texto substituindo espaços comuns por *qualquer* caractere Zs visualmente idêntico, então cobertura parcial é fácil de contornar.

## Detecção de homoglyph

`nowatermark detect` também sinaliza palavras que misturam letras latinas com Cirílico ou Grego visualmente idênticos (ex: um `а` cirílico no lugar de um `a` latino). É uma técnica real pra esconder payload sem nenhum caractere invisível, e [pesquisa independente sobre a onda de ferramentas de remoção de watermark de IA de agosto de 2026](https://www.bleepingcomputer.com/news/security/ai-watermark-removers-flood-the-web-almost-none-can-prove-they-work/) confirma que ela está em uso.

O relatório aparece separado e nunca afeta o exit code do `detect`. Misturar scripts dentro de uma palavra é raro em texto legítimo mas não impossível, então trate como sinal pra checar, não como achado. O `clean` não mexe nessas palavras, porque reescrever caractere visível é uma garantia diferente, mais arriscada, do que remover invisível (acompanhado no [TODO IMPROVEMENTS.md](TODO%20IMPROVEMENTS.md)).

## Segurança de emoji

ZWJ/ZWNJ e caracteres do bloco de tag também são usados legitimamente em emoji (sequências de família/casal, sequências de bandeira) e em alguns idiomas (ZWNJ em texto índico). Por padrão, o `nowatermark clean` não remove esses caracteres quando estão ao lado de codepoints de emoji ou dentro de uma sequência válida de bandeira-emoji. Passe `--no-emoji-guard` pra remover incondicionalmente.

O `detect` reporta todo caractere candidato que encontra, inclusive um ZWJ dentro de uma sequência de emoji. Um emoji de família, por exemplo, lista três caracteres ZERO WIDTH JOINER, e o `clean` mantém eles. Então o `detect` pode sair com `1` num texto que o `clean` deixa como está. Leia o relatório antes de agir pelo exit code.

## Skill de agente

`skill/SKILL.md` empacota isso como uma skill instalável para agentes de IA que suportam o formato SKILL.md. Coloque no diretório de skills do seu agente e ele detecta e limpa marcas d'água em texto automaticamente durante uma sessão. A skill também chama a skill `stop-slop` pra limpeza estilística do texto.

## Desenvolvimento

```bash
git clone https://github.com/obrenoalvim/no-watermark.git
cd no-watermark
pip install -e ".[dev]"
pytest -v
```

---

## Perguntas frequentes

**Ele remove marcas d'água estatísticas de texto de IA?**
Não. Elas vivem na escolha das palavras, não nos caracteres. Remover exige reescrever o texto, e nenhuma ferramenta pode prometer um resultado limpo.

**Vai quebrar meus emojis ou texto não latino?**
O `clean` mantém ZWJ e sequências de bandeira ao lado de emoji por padrão. ZWJ e ZWNJ também aparecem legitimamente em alguns idiomas (ZWNJ em texto índico), então confira a saída do `--report` antes de limpar texto nesses idiomas.

**Por que o `detect` sai com 1 num texto que parece normal?**
Caracteres invisíveis são invisíveis. Rode o `detect` pra ver exatamente quais codepoints ele achou e onde estão.

## Projetos relacionados

[guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) é um app open-source popular nessa área. Cruzar a cobertura com ele adicionou a Área de Uso Privado aqui e reforçou a checagem de preservação de bandeira-emoji.

## Mais skills para Claude Code do mesmo autor

- [**zero-drift**](https://github.com/obrenoalvim/zero-drift): mantém sessões longas ancoradas com respostas com nome e um `TASK.md` vivo.
- [**keep-improving**](https://github.com/obrenoalvim/keep-improving): loop autônomo de melhoria com um painel de revisão de dez papéis.
- [**unblock**](https://github.com/obrenoalvim/unblock): cadeia gratuita de 13 ferramentas para pesquisa web que continua tentando.
- [**findable**](https://github.com/obrenoalvim/findable): pesquisa de SEO e GEO que aplica as correções seguras.

## Contribuindo

Achou uma classe de caractere que escapa, ou uma sequência legítima que é removida? Abra uma issue ou um PR. Veja o [CONTRIBUTING.pt-BR.md](CONTRIBUTING.pt-BR.md) e o [changelog](CHANGELOG.md).

## Licença

[MIT](LICENSE)

---

<div align="center">

Se o no-watermark achou algo escondido no seu texto, uma ⭐ ajuda outras pessoas a encontrá-lo também.

<sub>**Tópicos:** unicode · zero-width-characters · invisible-characters · watermark · steganography · ascii-smuggling · prompt-injection · text-sanitizer · cli · python · security · claude-skill</sub>

</div>
