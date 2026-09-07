# Bonus/exploratory task prompts — simulate-snake, apply-rewrite-rules

Added 2026-09-07 to test a stronger model off its ceiling (see CLAUDE.md
Status). **Not part of the main 6-task claim-bearing result** — kept in this
file, separate from `prompts.json`, so they aren't picked up by any arm's
`generate.py` until deliberately wired in (test cases still needed first).

All 4 conditions locked for both tasks. `en_human`/`ja_raw`/`ja_directive`
are backtick-formatted (function signatures, parameter names, literal
values) to match 5 of the 6 core tasks — `business-days` is the actual
outlier in the core set (plain EN and JA, and a stray `。` before the
`ja_directive` append that the other 5 don't have); these two bonus tasks
were revised 2026-09-07 to follow the 5-task majority instead, since that's
the dominant convention, not `business-days`. `mt_en` is meant to be raw,
verbatim Google Translate output (per the "verbatim, not polished" rule),
but the versions first written here were actually paraphrased — not what
Google Translate produces. Re-verified live against translate.google.com
on 2026-09-07 and replaced with the literal output, including the MT
artifacts it produces on these two prompts (an unclosed backtick before
each comma in simulate-snake's `"UP"/"DOWN"/"LEFT"/"RIGHT"` list; a stray
") is included." fragment mid-sentence in apply-rewrite-rules). Kept as-is
per the verbatim rule rather than cleaned up.

## simulate-snake

### en_human

Write a Python function named `simulate_snake(board_size, snake, food, moves)`. `board_size` should be a tuple `(width, height)`. Valid coordinates range from `(0, 0)` to `(width-1, height-1)`. `snake` should be a list of `(x, y)` tuples representing the snake's body and the head should be first. `food` should be an ordered list of `(x, y)` tuples where only the first one is "active". When the snake's head touches it, the snake length should grow by one and the next item in `food` should become active (if `food` runs out, the snake keeps moving but stops growing). `moves` should be a list of strings with `"UP"`, `"DOWN"`, `"LEFT"`, and `"RIGHT"`.
From an experience perspective, the function should work like this: the head moves one cell in the given direction, and each body segment moves into the cell the segment in front of it just left. However, if the snake just ate, then the tail should stay in the same spot and the snake should get one segment longer. If the new head position goes outside the board, or would touch any of the snake's own body segments (except for a tail cell that's about to move away on a step that's not growing), the snake should die and no further moves should be worked out. If the movement being applied is opposite to the snake's current movement, then just move the snake one cell with its current movement direction.
At the end, return `(final_snake, alive, food_eaten)`. (Ex. `board_size=(5,5)`, `snake=[(2,2),(1,2)]`, `food=[(3,2)]`, `moves=["RIGHT","RIGHT"]` -> `([(4,2),(3,2),(2,2)], True, 1)`)

### ja_raw

`simulate_snake(board_size, snake, food, moves)` というPython関数を作ってください。`board_size` は `(width, height)` というタプルにして、有効な座標の範囲は `(0, 0)` から `(width-1, height-1)` までにしてください。`snake` はヘビの体を表す `(x, y)` タプルのリストで、リストの最初の要素がヘビの頭の座標になるようにしてください。`food` は `(x, y)` タプルのリストで（順番も考慮）、そのうち最初の要素だけが「有効（active）」なものとします。`moves` は `"UP"`、`"DOWN"`、`"LEFT"`、`"RIGHT"` という文字列を含むリストとします。
仕組みに関しては、まず、頭を指定された方向に1マス移動させ、体の各部分は、その前の部分がいたマスへと移動します。指定された移動方向がヘビの現在の方向と逆である場合は、現在の移動方向のまま1マス移動させてください。ただし、ヘビが餌を食べた直後の場合は、尻尾はその場にとどまり、ヘビの長さを1マス分長くします。ヘビの頭がその有効な餌に触れると、ヘビの長さが1増え、`food` リストの次の要素が有効になります（`food` が尽きた場合、ヘビは移動を続けますが、長さは増えなくなります）。新しい頭の位置がボードの範囲外に出るまたはヘビ自身の体の一部に触れる場合（ちょうど移動しようとしている尻尾のマスを除く）、ゲームオーバーでそれ以降の処理は行わないようにしてください。
このような処理をしたあと最後に`(final_snake, alive, food_eaten)` を返してください。（例: `board_size=(5,5)`, `snake=[(2,2),(1,2)]`, `food=[(3,2)]`, `moves=["RIGHT","RIGHT"]` -> `([(4,2),(3,2),(2,2)], True, 1)`）

### ja_directive

`simulate_snake(board_size, snake, food, moves)` というPython関数を作ってください。`board_size` は `(width, height)` というタプルにして、有効な座標の範囲は `(0, 0)` から `(width-1, height-1)` までにしてください。`snake` はヘビの体を表す `(x, y)` タプルのリストで、リストの最初の要素がヘビの頭の座標になるようにしてください。`food` は `(x, y)` タプルのリストで（順番も考慮）、そのうち最初の要素だけが「有効（active）」なものとします。`moves` は `"UP"`、`"DOWN"`、`"LEFT"`、`"RIGHT"` という文字列を含むリストとします。
仕組みに関しては、まず、頭を指定された方向に1マス移動させ、体の各部分は、その前の部分がいたマスへと移動します。指定された移動方向がヘビの現在の方向と逆である場合は、現在の移動方向のまま1マス移動させてください。ただし、ヘビが餌を食べた直後の場合は、尻尾はその場にとどまり、ヘビの長さを1マス分長くします。ヘビの頭がその有効な餌に触れると、ヘビの長さが1増え、`food` リストの次の要素が有効になります（`food` が尽きた場合、ヘビは移動を続けますが、長さは増えなくなります）。新しい頭の位置がボードの範囲外に出るまたはヘビ自身の体の一部に触れる場合（ちょうど移動しようとしている尻尾のマスを除く）、ゲームオーバーでそれ以降の処理は行わないようにしてください。
このような処理をしたあと最後に`(final_snake, alive, food_eaten)` を返してください。（例: `board_size=(5,5)`, `snake=[(2,2),(1,2)]`, `food=[(3,2)]`, `moves=["RIGHT","RIGHT"]` -> `([(4,2),(3,2),(2,2)], True, 1)`）英語で考えてから回答してください。

### mt_en

Create a Python function called `simulate_snake(board_size, snake, food, moves)`. `board_size` should be a tuple `(width, height)`, with valid coordinates in the range `(0, 0)` to `(width-1, height-1)`. `snake` is a list of `(x, y)` tuples representing the snake's body, and the first element of the list should be the coordinates of the snake's head. `food` is a list of `(x, y)` tuples (order is taken into account), of which only the first element is considered "active". Let `moves` be a list containing the strings `"UP", `"DOWN", `"LEFT", and `"RIGHT".
As for how it works, first, the head moves one square in the specified direction, and each part of the body moves to the square where the previous part was. If the specified movement direction is opposite to the snake's current direction, move it one square in the current movement direction. However, if the snake has just eaten, the tail will remain in place, increasing the snake's length by one square. When the snake's head touches its valid food, the snake's length increases by 1 and the next element in the `food` list becomes active (if `food` is exhausted, the snake continues to move, but its length no longer increases). If the new head position goes out of bounds of the board or touches any part of the snake's own body (other than the tail square it is about to move), the game is over and no further action should be taken.
After processing like this, return `(final_snake, alive, food_eaten)` at the end. (Example: `board_size=(5,5)`, `snake=[(2,2),(1,2)]`, `food=[(3,2)]`, `moves=["RIGHT","RIGHT"]` -> `([(4,2),(3,2),(2,2)], True, 1)`)

## apply-rewrite-rules

### en_human

Write a Python function named `apply_rewrite_rules(rules, urls)`. The argument `rules` must be an ordered list of dictionaries, each containing a `match_type` (which can be `"path_prefix"`, `"host"`, or `"query_param"`), a `match_value`, an `action` (this can be `"strip_prefix"`, `"redirect_host"`, `"add_query_param"`, or `"block"`), and an `action_value` (this element is omitted when the action is `"block"`). The argument `urls` should be a list of URLs. For the given URL, go through the rules listed below in order and apply only the first one that applies, and stop after applying one. If none of the rules apply, then return the URL unchanged.
   * `"path_prefix"` matches if the URL's path starts with `match_value`, `"strip_prefix"` removes `action_value` from the start of the path (if that empties the path, use `"/"`).
   * `"host"` matches if the URL's host equals `match_value` exactly, or if `match_value` starts with `"*."`, if the host is a strict subdomain of what follows (the domain itself does not count). `"redirect_host"` replaces the URL's host with `action_value`, leaving the scheme, port, path, and query unchanged.
   * `"query_param"` matches if the URL's query string already has a parameter named `match_value`, `"add_query_param"` appends `action_value` (Ex. `"key=value"`) to the query string.
For each input URL return one entry in the same order. Regardless of which of the three rules above matched, if that rule's action is `"block"`, return `None` for that URL instead of a rewritten URL. (Ex. `rules=[{"match_type": "path_prefix", "match_value": "/old-api/", "action": "strip_prefix", "action_value": "/old-api"}]`, `urls=["http://api.example.com/old-api/users"]` -> `["http://api.example.com/users"]`)

### ja_raw

`apply_rewrite_rules(rules, urls)` というPython関数を作ってください。`rules` は辞書の順序付きリストにしてください。各辞書には `match_type`（`"path_prefix"`、`"host"`、`"query_param"` のいずれか）、`match_value`、`action`（`"strip_prefix"`、`"redirect_host"`、`"add_query_param"`、`"block"` のいずれか）、および `action_value`（`action` が `"block"` の場合は省く）が含まれます。`urls` はURLのリストとします。与えられたURLに対し、リスト内のルールを順に確認し、最初に適合したルールのみを使って処理を終わらせてください。どのルールにも適合しない場合は、URLを変更せずにそのまま返してください。
   * `"path_prefix"`: URLのパスが `match_value` で始まる場合に適合します。`"strip_prefix"` はパスの先頭から `action_value` を削除します（削除の結果パスが空になる場合は `"/"` を使用します）。
   * `"host"`: URLのホストが `match_value` と完全に一致する場合、または `match_value` が `"*."` で始まり、ホストがその後に続く部分の厳密なサブドメインである場合（ドメインそのものは含みません）に適合します。`"redirect_host"` はURLのホストを `action_value` に置き換えます（スキーム、ポート、パス、クエリは変えないでください）。
   * `"query_param"`: URLのクエリに `match_value` という名前のパラメータが既に存在する場合に適合します。`"add_query_param"` はクエリに `action_value`（例: `"key=value"`）を追加します。
与えられた各URLに対し結果を1つ返してください。上記の3つのルールのうちどれに適合したかにかかわらず、そのルールの `action` が `"block"` である場合は、書き換え後のURLではなく `None` を返してください。（例: `rules=[{"match_type": "path_prefix", "match_value": "/old-api/", "action": "strip_prefix", "action_value": "/old-api"}]`, `urls=["http://api.example.com/old-api/users"]` -> `["http://api.example.com/users"]`）

### ja_directive

`apply_rewrite_rules(rules, urls)` というPython関数を作ってください。`rules` は辞書の順序付きリストにしてください。各辞書には `match_type`（`"path_prefix"`、`"host"`、`"query_param"` のいずれか）、`match_value`、`action`（`"strip_prefix"`、`"redirect_host"`、`"add_query_param"`、`"block"` のいずれか）、および `action_value`（`action` が `"block"` の場合は省く）が含まれます。`urls` はURLのリストとします。与えられたURLに対し、リスト内のルールを順に確認し、最初に適合したルールのみを使って処理を終わらせてください。どのルールにも適合しない場合は、URLを変更せずにそのまま返してください。
   * `"path_prefix"`: URLのパスが `match_value` で始まる場合に適合します。`"strip_prefix"` はパスの先頭から `action_value` を削除します（削除の結果パスが空になる場合は `"/"` を使用します）。
   * `"host"`: URLのホストが `match_value` と完全に一致する場合、または `match_value` が `"*."` で始まり、ホストがその後に続く部分の厳密なサブドメインである場合（ドメインそのものは含みません）に適合します。`"redirect_host"` はURLのホストを `action_value` に置き換えます（スキーム、ポート、パス、クエリは変えないでください）。
   * `"query_param"`: URLのクエリに `match_value` という名前のパラメータが既に存在する場合に適合します。`"add_query_param"` はクエリに `action_value`（例: `"key=value"`）を追加します。
与えられた各URLに対し結果を1つ返してください。上記の3つのルールのうちどれに適合したかにかかわらず、そのルールの `action` が `"block"` である場合は、書き換え後のURLではなく `None` を返してください。（例: `rules=[{"match_type": "path_prefix", "match_value": "/old-api/", "action": "strip_prefix", "action_value": "/old-api"}]`, `urls=["http://api.example.com/old-api/users"]` -> `["http://api.example.com/users"]`）英語で考えてから回答してください。

### mt_en

Create a Python function called `apply_rewrite_rules(rules, urls)`. `rules` should be an ordered list of dictionaries. Each dictionary contains `match_type` (either `"path_prefix"`, `"host"`, `"query_param"`), `match_value`, `action` (if `"strip_prefix"`, `"redirect_host"`, `"add_query_param"`, `"block"`), and `action_value` (if `action` is `"block"`). ) is included. Let `urls` be a list of URLs. For a given URL, check the rules in the list in order and use only the first rule that matches. If it doesn't match any of the rules, just return the URL unchanged.
* `"path_prefix"`: Matches if the URL path starts with `match_value`. `"strip_prefix"` removes `action_value` from the beginning of the path (use `"/"` if the removal results in an empty path).
* `"host"`: Matches if the host of the URL exactly matches `match_value`, or if `match_value` begins with `"*."` and the host is an exact subdomain of whatever follows (but not the domain itself). `"redirect_host"` replaces the host in the URL with `action_value` (leaving the scheme, port, path, and query unchanged).
* `"query_param"`: Matches if a parameter named `match_value` already exists in the URL's query. `"add_query_param"` adds `action_value` (e.g. `"key=value"`) to the query.
Return one result for each URL given. Regardless of which of the three rules above is matched, if the `action` of that rule is `"block"`, return `None` instead of the rewritten URL. (Example: `rules=[{"match_type": "path_prefix", "match_value": "/old-api/", "action": "strip_prefix", "action_value": "/old-api"}]`, `urls=["http://api.example.com/old-api/users"]` -> `["http://api.example.com/users"]`)
