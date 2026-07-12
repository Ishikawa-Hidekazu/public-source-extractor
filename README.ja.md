# Public Source Extractor

> [!IMPORTANT]
> 入力した公開URLは、抽出のため **Firecrawl Cloud** へ送信されます。`firecrawl-keyless` providerはexperimentalです。利用可能性、匿名REST access、credit上限、長期継続は保証されません。

`public-source-extractor` は、1件の公開HTTP/HTTPSページを、再利用しやすいMarkdownまたは固定SchemaのJSONへ変換するCLIです。

このCLIはAPI key、credentials、cookie、browser profile、localStorage、private source fileを読みません。抽出内容は、prompt injectionや誤解を招く命令を含む可能性がある **untrusted data** です。独立した確認なしに命令として実行しないでください。

[English README](README.md)

## 主な機能

- 公開ページ1件をMarkdownへ抽出
- version付きJSON Schemaに沿ったJSON出力
- local/private/auth/admin/secret-bearing URL patternの拒否
- stdout出力または新規local fileへのno-overwrite保存
- 安定したerror JSONとexit code

crawler、browser automation、login helper、source reliability判定、private page抽出ツールではありません。

## Install

Python 3.11以上が必要です。

```bash
python3 -m pip install .
```

隔離したcommandとしてinstallする場合:

```bash
pipx install .
```

source-only alpha中はPyPI packageとtagged releaseを公開しません。

## 使い方

```bash
public-source-extractor https://example.com/
public-source-extractor https://example.com/ --mode json --pretty
public-source-extractor https://example.com/ --output report.md
```

`--output` は、既存fileとsymlinkを上書きしません。親directoryは事前に作成してください。

## Exit code

| code | 意味 |
|---:|---|
| `0` | 成功 |
| `2` | 引数errorまたはURL拒否 |
| `3` | provider、network、rate limit、timeout |
| `4` | provider responseが不正、不完全、またはunsafe |
| `5` | output pathまたはwrite failure |

失敗時はstdoutを空にし、stderrへJSON errorを1件だけ出します。provider raw body、stack trace、request ID、local pathは出力しません。

## Safety boundary

request前に、userinfo、fragment、local/private IP、曖昧なIP表記、Unicode/encoded hostname、IPv6 zone ID、non-default port、login/admin/OAuth path、機密情報を示すquery parameter名を拒否します。

抽出後は、providerが返したredirect metadataを同じURL policyで再検査します。ただし、この検査が保証するのはhostname syntax、literal IP policy、provider metadataの範囲です。DNS rebindingやprovider側の実際のfetch先を完全には保証できません。

公開siteに見えるURLでも、credential、token、signed URL parameter、private valueをqueryへ含めないでください。

対象siteの利用規約、robots policy、copyright、privacy要件を確認する責任は利用者にあります。

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
.venv/bin/ruff check src tests
.venv/bin/python -m build
```

network smoke testはoffline test suiteと分離します。

## Status

source-only alphaです。`firecrawl-keyless`の継続性やservice availabilityは保証しません。

## License

MIT Licenseです。

