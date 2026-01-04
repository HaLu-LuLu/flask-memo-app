from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)
MEMO_FILE = "memo.txt"

@app.route("/")
def index():
    # 検索キーワードを（前後の空白を削除しておく）
    query = request.args.get("q", "").strip()

    # 完了を隠すチェックボックス
    hide_done = request.args.get("hide_done", "")
    # タグフィルター（重要／緊急／低／買い物など）
    selected_tag = request.args.get("tag", "").strip()

    edited = request.args.get("edited")

    msg = request.args.get("msg")
    
    # メモ全件を読み込み
    memos = []
    if os.path.exists(MEMO_FILE):
        with open(MEMO_FILE, "r", encoding="utf-8") as f:
            memos = f.readlines()

    items = list(enumerate(memos))

    filtered = items

# 検索
    if query:
        if query == "完了":
            filtered = [(i, m) for (i, m) in items if "[完了]" in m]
        elif query == "未完了":
            filtered = [(i, m) for (i, m) in items if "[完了]" not in m]
        else:
            filtered = [(i, m) for (i, m) in items if query in m]

# タグ
    if selected_tag:
        filtered = [(i, m) for (i, m) in filtered if selected_tag in m]

# 完了を隠す
    if hide_done == "1":
        filtered = [(i, m) for (i, m) in filtered if "[完了]" not in m]

# 並び替え（未完了）→完了
    not_done = [(i, m) for (i, m) in filtered if "[完了]" not in m]
    done = [(i, m) for (i, m) in filtered if "[完了]" in m]
    memos_to_show = not_done + done

    return render_template("index.html", memos=memos_to_show, serch_query=query, hide_done=hide_done, selected_tag=selected_tag, edited=edited, msg=msg)

@app.route("/add", methods=["POST"])
def add_memo():
    memo_text = request.form.get("memo", "").strip()
    tag = request.form.get("tag","").strip()

    if memo_text:
        now = datetime.now() .strftime("%Y-%m-%d %H:%M")

        # ベースのテキスト（日時＋メモ本文）
        text = f"[{now}] {memo_text}"

        # タグがタグなし以外なら追記
        if tag and tag != "タグなし":
            text += f" | {tag}"

        with open(MEMO_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")
            
    return redirect(url_for("index", msg="added"))

@app.route("/delete/<int:index>", methods=["POST"])
def delete_memo(index):
    if os.path.exists(MEMO_FILE):
        with open(MEMO_FILE, "r", encoding="utf-8") as f:
            memos = f.readlines()


        if 0 <= index < len(memos):
            del memos[index] #指定された行を削除
            
        with open(MEMO_FILE, "w", encoding="utf-8")as f:
            f.writelines(memos)

    return redirect(url_for("index"))

@app.route("/toggle_done/<int:index>", methods=["POST"])
def toggle_done(index):
    #メモファイルがなければ何もしないで一覧へ
    if not os.path.exists(MEMO_FILE):
        return redirect(url_for("index"))
    
    #すべてのメモを読み込む
    with open(MEMO_FILE, "r", encoding="utf-8") as f:
        memos = f.readlines()

    #指定された行を「完了⇔未完了」で切り替え
    if not 0 <= index < len(memos):
        return redirect(url_for("index"))
    
    line = memos[index].rstrip("\n")

    DONE_TOKEN = "[完了]"

    #すでに［完了］が付いているなら外す
    if DONE_TOKEN in line:
        line = line.replace(DONE_TOKEN, "").rstrip()
    else:
    #付いていなければ松尾に［完了］を追加
        line = f"{line} {DONE_TOKEN}".rstrip()

    memos[index] = line + "\n"

        #上書き保存
    with open(MEMO_FILE, "w", encoding="utf-8") as f:
        f.writelines(memos)

    return redirect(url_for("index", msg="toggled"))

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_memo(index):
    #全メモ読み込み
    if not os.path.exists(MEMO_FILE):
        return redirect(url_for("index"))
    
    with open(MEMO_FILE, "r", encoding="utf-8") as f:
        memos = f.readlines()

    if not (0 <= index < len(memos)):
        return redirect(url_for("index"))
    
    original = memos[index].rstrip("\n")
    
    date_prefix = ""
    rest = original

    if original.startswith("[") and "]" in original:
        date_prefix = original[:original.index("]")+1]
        rest = original[original.index("]")+1:].strip()

        tag = ""
        text = rest
        
    if rest.startswith("[") and "]" in rest:
        tag = rest[1:rest.index("]")]
        text = rest[rest.index("]")+1:].strip()

    if request.method == "POST":
        new_text = request.form.get("memo", "").strip()
        new_tag = request.form.get("tag", "").strip()

        if new_text:
            if new_tag:
                memos[index] = f"{date_prefix}[{new_tag}]{new_text}\n"
            else:
                memos[index] = f"{date_prefix}{new_text}\n"

            with open(MEMO_FILE, "w", encoding="utf=8") as f:
                f.writelines(memos)
                
        return redirect(url_for("index", edited=index, msg="saved"))

    return render_template("edit.html", index=index, text=text, tag=tag)

@app.route("/foods")
def foods():
    food_list = ["寿司", "ラーメン", "カレー", "ハンバーグ"]

    return render_template("foods.html", foods=food_list)

@app.route("/check", methods=["GET", "POST"])
def check():
    score = None
    result = None

    if request.method == "POST":
        score = request.form.get("score")
        if score:
            score = int(score)
            if score >= 60:
                result = "合格！🎉"
            else:
                result = "不合格…💦"

    return render_template("check.html", score=score, result=result)

if __name__ == "__main__":
    app.run(debug=True)




