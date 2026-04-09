"""
パイロット実験用プロンプトテンプレート

各プロンプトは、LLMに対して「回答」と「信頼度（0〜100の整数）」を
同時に出力させるフォーマットを指定する。
"""

BASIC_PROMPT_JA = """あなたは質問に答えるアシスタントです。
以下の問題に回答してください。さらに、自分の回答が正しい確率を
0〜100の整数で表してください。0は「まったく自信がない」、
100は「絶対に正しいと確信している」を意味します。

問題:
{question}
{choices_section}
以下の形式で、必ずこの通りに出力してください。
他の余計な文章は出力しないでください。

回答: <ここに回答>
信頼度: <0〜100の整数>
"""


BASIC_PROMPT_EN = """You are a helpful assistant. Answer the following question,
then express how confident you are in your answer as an integer between 0 and 100.
0 means "completely uncertain" and 100 means "absolutely certain".

Question:
{question}
{choices_section}
Please output strictly in the following format. Do not include any other text.

Answer: <your answer>
Confidence: <integer 0-100>
"""


# 実験2用: 5段階スケール
SCALE5_PROMPT_JA = """あなたは質問に答えるアシスタントです。
以下の問題に回答し、自分の回答の確信度を1〜5の5段階で表してください。
1: 全く自信なし, 2: あまり自信なし, 3: どちらとも言えない,
4: まあまあ自信あり, 5: 非常に自信あり

問題:
{question}
{choices_section}
出力形式:
回答: <ここに回答>
信頼度: <1〜5の整数>
"""


# 実験2用: パーセント記法
PERCENT_PROMPT_JA = """以下の問題に回答し、その回答が正しいパーセントを
0%から100%の範囲で表してください。

問題:
{question}
{choices_section}
出力形式:
回答: <ここに回答>
信頼度: <XX%>
"""


# 実験2用: 自然言語表現
VERBAL_PROMPT_JA = """以下の問題に回答し、その回答に対する自信の度合いを
言葉で表してください（例: まったく自信がない、あまり自信がない、
どちらとも言えない、まあまあ自信がある、非常に自信がある）。

問題:
{question}
{choices_section}
出力形式:
回答: <ここに回答>
自信度: <言葉での表現>
"""


def build_prompt(template: str, question: str, choices: str | None = None) -> str:
    """プロンプトテンプレートに問題文と選択肢を埋め込んで完成させる"""
    if choices and choices.strip():
        choice_list = choices.split("|")
        choices_section = "\n選択肢:\n" + "\n".join(
            f"  {chr(ord('A') + i)}. {c}" for i, c in enumerate(choice_list)
        ) + "\n"
    else:
        choices_section = "\n"
    return template.format(question=question, choices_section=choices_section)


if __name__ == "__main__":
    # テスト出力
    sample = build_prompt(
        BASIC_PROMPT_JA,
        "りんごを食べる時に普通使う道具は何ですか?",
        "包丁|のこぎり|ハサミ|金槌"
    )
    print(sample)
