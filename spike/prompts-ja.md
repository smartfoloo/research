# Prompt text (Japanese) — final, human-authored

JA-raw prompts, written by the researcher (bilingual, calibrated against
native Japanese coding-problem sources), independently authored from the
task meaning — not translated from the EN prompts.

## Simple

1. **reverse-list-elements**

`elements` の順序を反転させる `reverse_list_elements(elements, punctuation)` という Python 関数を作ってください。その際、`punctuation` に含まれる記号を元の単語とセットにして `(new_elements, new_punctuation)` を返すようにしてください。（例: `elements=["Hello", "world"]`, `punctuation=["", "!"]` → `(["world", "Hello"], ["!", ""])`）

2. **business-days**

2つの日付の間の営業日（月曜日から金曜日）の数を返す `business_days(date1, date2)` という Python 関数を作ってください。日付はどちらも `YYYY-MM-DD` 形式です。祝日は考慮しなくて大丈夫です。ただし、2つの日付自体は含まないようにしてください。（例: "2024-01-01", "2024-01-08" → 4）。

3. **currency-format**

`n` の先頭に `$` を付け、3桁ごとにカンマで区切ったものを返す `format_currency(n)` という Python 関数を作ってください。負の数の場合は、ドル記号の前にマイナス記号を付けるようにしてください。（例: `4640039` → `"$4,640,039"`）

## Complex

4. **eval-expression**

`expr` の式を計算する `eval_expression(expr)` という Python 関数を作成してください。演算の順序を考慮し、負の数も計算できるようにしてください。ゼロで割る場合は、`ZeroDivisionError` を出すようにしてください。（例: `"3 + 4 * (2 - 1)"` → `7`）

5. **shortest-path**

最短の総距離と、その経路上のノードを並べたリスト `(distance, path)` を返す `shortest_path(edges, start, end)` という Python 関数を作成してください。`edges` は `(from_node, to_node, weight)` というタプルのリストで、一方通行の道を表しています。start と end が同じノードである場合、(0, [start]) を返してください。いずれかのエッジの weight がマイナスである場合は `ValueError` を出すようにしてください。経路が存在しない場合は `(None, None)` を返してください。（例: `edges=[("A","B",1), ("B","C",2), ("A","C",5)]`, `start="A"`, `end="C"` → `(3, ["A", "B", "C"])`）

6. **bank-rollback**

`bank_rollback(balance, transactions)` という Python 関数を作成してください。`transactions` は取引額を並べた数値のリストです。与えられた取引を順番に適用して、計算した最終的な残高を返すようにしてください。計算中でも残高がマイナスになる場合は、計算をやめて元の残高である `balance` を用いて `(balance, False)` を返してください。そうでない場合は、`(final_balance, True)` を返してください。（例：`balance=100, transactions=[50, -30, -200]` → `(100, False)`）
