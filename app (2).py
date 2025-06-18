import streamlit as st
import random
import re
import time

# 4文字の英単語リスト
FOUR_LETTER_WORDS = [
    "ABLE", "ACID", "AGED", "ALSO", "AREA", "ARMY", "AWAY", "BABY", "BACK", "BALL",
    "BAND", "BANK", "BASE", "BATH", "BEAR", "BEAT", "BEEN", "BELL", "BEST", "BILL",
    "BIRD", "BLOW", "BLUE", "BOAT", "BODY", "BONE", "BOOK", "BORN", "BOTH", "BOYS",
    "BUSY", "CALL", "CAME", "CAMP", "CARD", "CARE", "CARS", "CASE", "CASH", "CAST",
    "CELL", "CITY", "CLUB", "COAL", "COAT", "CODE", "COLD", "COME", "COOL", "COPY",
    "COST", "DARK", "DATA", "DATE", "DAYS", "DEAD", "DEAL", "DEAR", "DEEP", "DESK",
    "DOES", "DONE", "DOOR", "DOWN", "DRAW", "DREW", "DROP", "DRUG", "DUAL", "EACH",
    "EARL", "EARN", "EAST", "EASY", "EDGE", "ELSE", "EVEN", "EVER", "EVIL", "EYES",
    "FACE", "FACT", "FAIL", "FAIR", "FALL", "FARM", "FAST", "FEAR", "FEEL", "FEET",
    "FELL", "FELT", "FILE", "FILL", "FILM", "FIND", "FINE", "FIRE", "FIRM", "FISH",
    "FIVE", "FLAT", "FLOW", "FOOD", "FOOT", "FORM", "FORT", "FOUR", "FREE", "FROM",
    "FULL", "FUND", "GAME", "GAVE", "GIFT", "GIRL", "GIVE", "GLAD", "GOAL", "GOES",
    "GOLD", "GONE", "GOOD", "GRAY", "GREW", "GROW", "HAIR", "HALF", "HALL", "HAND",
    "HANG", "HARD", "HARM", "HEAD", "HEAR", "HEAT", "HELD", "HELL", "HELP", "HERE",
    "HIGH", "HILL", "HOLD", "HOLE", "HOME", "HOPE", "HOUR", "HUGE", "HUNG", "HURT",
    "IDEA", "INCH", "INTO", "IRON", "ITEM", "JACK", "JANE", "JULY", "JUMP", "JUNE",
    "JUST", "KEEP", "KEPT", "KILL", "KIND", "KING", "KNEW", "KNOW", "LACK", "LADY",
    "LAND", "LAST", "LATE", "LEAD", "LEFT", "LESS", "LIFE", "LIFT", "LIKE", "LINE",
    "LIST", "LIVE", "LOAN", "LOCK", "LONG", "LOOK", "LORD", "LOSE", "LOSS", "LOST",
    "LOTS", "LOVE", "MADE", "MAIL", "MAIN", "MAKE", "MALE", "MANY", "MARK", "MASS",
    "MEAL", "MEAN", "MEAT", "MEET", "MIND", "MINE", "MISS", "MODE", "MOON", "MORE",
    "MOST", "MOVE", "MUCH", "MUST", "NAME", "NEAR", "NECK", "NEED", "NEWS", "NEXT",
    "NICE", "NINE", "NODE", "NONE", "NOON", "NOTE", "NOUN", "ONLY", "OPEN", "ORAL",
    "OVER", "PACE", "PACK", "PAGE", "PAID", "PAIN", "PAIR", "PALE", "PARK", "PART",
    "PASS", "PAST", "PATH", "PEAK", "PICK", "PINK", "PLAN", "PLAY", "PLOT", "PLUS",
    "POEM", "POET", "POLL", "POOL", "POOR", "PORT", "POST", "PULL", "PURE", "PUSH",
    "RACE", "RAIN", "RANK", "RATE", "READ", "REAL", "REAR", "RELY", "RENT", "REST",
    "RICH", "RIDE", "RING", "RISE", "RISK", "ROAD", "ROCK", "ROLE", "ROLL", "ROOM",
    "ROOT", "ROSE", "RULE", "RUNS", "SAFE", "SAID", "SAIL", "SALE", "SALT", "SAME",
    "SAND", "SAVE", "SEAT", "SEED", "SEEK", "SEEM", "SEEN", "SELF", "SELL", "SEND",
    "SENT", "SHIP", "SHOP", "SHOT", "SHOW", "SHUT", "SICK", "SIDE", "SIGN", "SING",
    "SITE", "SIZE", "SKIN", "SLIP", "SLOW", "SNOW", "SOFT", "SOIL", "SOLD", "SOME",
    "SONG", "SOON", "SORT", "SOUL", "SPOT", "STAR", "STAY", "STEP", "STOP", "SUCH",
    "SUIT", "SURE", "TAKE", "TALK", "TALL", "TANK", "TAPE", "TASK", "TEAM", "TELL",
    "TERM", "TEST", "TEXT", "THAN", "THAT", "THEM", "THEN", "THEY", "THIN", "THIS",
    "THUS", "TILL", "TIME", "TINY", "TOLD", "TONE", "TOOK", "TOOL", "TOPS", "TOWN",
    "TREE", "TRIP", "TRUE", "TURN", "TYPE", "UNIT", "UPON", "USED", "USER", "VARY",
    "VAST", "VERY", "VIEW", "VOTE", "WAGE", "WAIT", "WAKE", "WALK", "WALL", "WANT",
    "WARM", "WASH", "WAVE", "WAYS", "WEAK", "WEAR", "WEEK", "WELL", "WENT", "WERE",
    "WEST", "WHAT", "WHEN", "WHOM", "WIDE", "WIFE", "WILD", "WILL", "WIND", "WINE",
    "WING", "WIRE", "WISE", "WISH", "WITH", "WOOD", "WORD", "WORE", "WORK", "YARD",
    "YEAR", "YOUR", "ZERO", "ZONE"
]

def get_random_word():
    """ランダムな4文字単語を選択"""
    return random.choice(FOUR_LETTER_WORDS)

def is_valid_word(word):
    """単語が有効かチェック"""
    return word.upper() in FOUR_LETTER_WORDS

def evaluate_guess(guess, target):
    """推測を評価して結果を返す"""
    result = []
    target_array = list(target)
    guess_array = list(guess.upper())
    
    # まず正確な位置をチェック
    for i in range(4):
        if guess_array[i] == target_array[i]:
            result.append('correct')
            target_array[i] = None  # マークして重複を避ける
            guess_array[i] = None
        else:
            result.append(None)
    
    # 次に含まれているが位置が違う文字をチェック
    for i in range(4):
        if guess_array[i] is not None:
            if guess_array[i] in target_array:
                result[i] = 'present'
                target_array[target_array.index(guess_array[i])] = None
            else:
                result[i] = 'absent'
    
    return result

def initialize_game():
    """ゲームを初期化"""
    if 'target_word' not in st.session_state:
        st.session_state.target_word = get_random_word()
    if 'guesses' not in st.session_state:
        st.session_state.guesses = []
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'won' not in st.session_state:
        st.session_state.won = False
    if 'current_input' not in st.session_state:
        st.session_state.current_input = ""
    if 'games_played' not in st.session_state:
        st.session_state.games_played = 0
    if 'games_won' not in st.session_state:
        st.session_state.games_won = 0
    if 'current_streak' not in st.session_state:
        st.session_state.current_streak = 0
    if 'max_streak' not in st.session_state:
        st.session_state.max_streak = 0

def reset_game():
    """ゲームをリセット"""
    # 統計を更新
    if st.session_state.game_over:
        st.session_state.games_played += 1
        if st.session_state.won:
            st.session_state.games_won += 1
            st.session_state.current_streak += 1
            st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.current_streak)
        else:
            st.session_state.current_streak = 0
    
    # ゲーム状態をリセット
    st.session_state.target_word = get_random_word()
    st.session_state.guesses = []
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.current_input = ""

def get_letter_status(letter, guesses):
    """文字の状態を取得（キーボード表示用）"""
    best_status = 'unused'
    for guess, result in guesses:
        for i, (guess_letter, status) in enumerate(zip(guess, result)):
            if guess_letter == letter:
                if status == 'correct':
                    return 'correct'  # 正解は最優先
                elif status == 'present' and best_status != 'correct':
                    best_status = 'present'
                elif status == 'absent' and best_status == 'unused':
                    best_status = 'absent'
    return best_status

def display_virtual_keyboard():
    """仮想キーボードを表示"""
    st.markdown("### 🎹 仮想キーボード")
    
    keyboard_rows = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
    ]
    
    for row_idx, row in enumerate(keyboard_rows):
        # 中央揃えのために適切な列数を計算
        if row_idx == 1:  # 中段は少し右にずらす
            cols = st.columns([0.5] + [1] * len(row) + [0.5])
            start_idx = 1
        else:
            cols = st.columns(len(row))
            start_idx = 0
        
        for i, letter in enumerate(row):
            with cols[start_idx + i]:
                status = get_letter_status(letter, st.session_state.guesses)
                
                # ボタンのスタイルを決定
                if status == 'correct':
                    button_type = "primary"
                    emoji = "✅"
                elif status == 'present':
                    button_type = "secondary"
                    emoji = "🟨"
                elif status == 'absent':
                    button_type = "secondary"
                    emoji = "❌"
                else:
                    button_type = "secondary"
                    emoji = ""
                
                button_text = f"{emoji} {letter}" if emoji else letter
                
                if st.button(
                    button_text,
                    key=f"key_{letter}",
                    disabled=st.session_state.game_over,
                    help=f"文字 {letter} を入力",
                    type=button_type,
                    use_container_width=True
                ):
                    if len(st.session_state.current_input) < 4:
                        st.session_state.current_input += letter
                        st.rerun()
    
    # 特殊キー
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⌫ 削除", disabled=st.session_state.game_over, type="secondary", use_container_width=True):
            if st.session_state.current_input:
                st.session_state.current_input = st.session_state.current_input[:-1]
                st.rerun()
    
    with col2:
        st.markdown(f"**現在の入力:** `{st.session_state.current_input + '＿' * (4 - len(st.session_state.current_input))}`")
    
    with col3:
        send_disabled = st.session_state.game_over or len(st.session_state.current_input) != 4
        if st.button("📤 送信", disabled=send_disabled, type="primary", use_container_width=True):
            process_guess(st.session_state.current_input)

def process_guess(guess):
    """推測を処理"""
    guess = guess.upper()
    
    if len(guess) != 4:
        st.error("4文字の単語を入力してください")
        return
    
    if not re.match("^[A-Z]+$", guess):
        st.error("英字のみを入力してください")
        return
    
    if not is_valid_word(guess):
        st.error("有効な英単語を入力してください")
        return
    
    # 推測を処理
    result = evaluate_guess(guess, st.session_state.target_word)
    st.session_state.guesses.append((guess, result))
    st.session_state.current_input = ""
    
    # ゲーム終了判定
    if guess == st.session_state.target_word:
        st.session_state.won = True
        st.session_state.game_over = True
    elif len(st.session_state.guesses) >= 6:
        st.session_state.game_over = True
    
    st.rerun()

def display_statistics():
    """統計情報を表示"""
    if st.session_state.games_played > 0:
        win_rate = (st.session_state.games_won / st.session_state.games_played) * 100
    else:
        win_rate = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("プレイ回数", st.session_state.games_played)
    
    with col2:
        st.metric("勝率", f"{win_rate:.1f}%")
    
    with col3:
        st.metric("現在の連勝", st.session_state.current_streak)
    
    with col4:
        st.metric("最高連勝", st.session_state.max_streak)

def main():
    st.set_page_config(
        page_title="4文字Wordle",
        page_icon="🎯",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # カスタムCSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f2937;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .game-stats {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .game-board {
        margin: 2rem 0;
        padding: 1rem;
        background: rgba(255,255,255,0.9);
        border-radius: 1rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .letter-box {
        display: inline-block;
        width: 60px;
        height: 60px;
        line-height: 60px;
        text-align: center;
        margin: 2px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 24px;
        border: 2px solid #d1d5db;
        transition: all 0.3s ease;
    }
    .current-input {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        letter-spacing: 1rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    .keyboard-section {
        background: rgba(255,255,255,0.95);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    .celebration {
        animation: bounce 0.6s ease-in-out infinite alternate;
    }
    @keyframes bounce {
        from { transform: translateY(0px); }
        to { transform: translateY(-10px); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ゲーム初期化
    initialize_game()
    
    # タイトル
    st.markdown('<h1 class="main-header">🎯 4文字Wordle</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.3rem; color: #6b7280; margin-bottom: 2rem;">4文字の英単語を6回以内で当てよう！ 🚀</p>', unsafe_allow_html=True)
    
    # 統計情報
    with st.container():
        st.markdown('<div class="game-stats">', unsafe_allow_html=True)
        st.markdown("### 📊 統計情報")
        display_statistics()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ゲーム制御
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 新しいゲーム", type="primary", use_container_width=True):
            reset_game()
            st.rerun()
    
    # 現在の入力表示
    if not st.session_state.game_over and st.session_state.current_input:
        current_display = st.session_state.current_input + "＿" * (4 - len(st.session_state.current_input))
        st.markdown(f'<div class="current-input">{current_display}</div>', unsafe_allow_html=True)
    
    # ゲームボード表示
    with st.container():
        st.markdown('<div class="game-board">', unsafe_allow_html=True)
        display_game_board()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 仮想キーボード
    if not st.session_state.game_over:
        with st.container():
            st.markdown('<div class="keyboard-section">', unsafe_allow_html=True)
            display_virtual_keyboard()
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 手動入力フォーム
    if not st.session_state.game_over:
        st.markdown("---")
        st.markdown("### ⌨️ 直接入力")
        with st.form("guess_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                manual_guess = st.text_input(
                    "4文字の英単語を入力:",
                    max_chars=4,
                    placeholder="例: WORD",
                    value="",
                    label_visibility="collapsed"
                ).upper()
            
            with col2:
                submitted = st.form_submit_button("推測する", type="primary", use_container_width=True)
            
            if submitted and manual_guess:
                process_guess(manual_guess)
    
    # ゲーム終了メッセージ
    if st.session_state.game_over:
        st.markdown("---")
        if st.session_state.won:
            st.markdown('<div class="celebration">', unsafe_allow_html=True)
            st.success(f"🎉 おめでとうございます！{len(st.session_state.guesses)}回で正解しました！")
            st.markdown('</div>', unsafe_allow_html=True)
            st.balloons()
            
            # 成績に応じたメッセージ
            attempts = len(st.session_state.guesses)
            if attempts == 1:
                st.info("🏆 完璧！一発で当てるなんて素晴らしい！")
            elif attempts <= 2:
                st.info("🥇 優秀！とても良い成績です！")
            elif attempts <= 3:
                st.info("🥈 良い成績！なかなかの推理力ですね！")
            elif attempts <= 4:
                st.info("🥉 まずまず！もう少しで完璧でした！")
            else:
                st.info("👏 お疲れ様！最後まで諦めずに頑張りました！")
        else:
            st.error(f"😔 残念... 正解は「**{st.session_state.target_word}**」でした。")
            st.info("💪 次回はきっと当てられますよ！")
        
        st.info("「新しいゲーム」ボタンで再挑戦できます！")
    
    # プログレスバー
    if not st.session_state.game_over:
        progress = len(st.session_state.guesses) / 6
        st.progress(progress, text=f"進行状況: {len(st.session_state.guesses)}/6 回")
    
    # ルール説明
    with st.expander("📖 ゲームのルール"):
        st.markdown("""
        **🎯 目標:**
        - 4文字の英単語を6回以内で当ててください
        
        **🎮 操作方法:**
        - 🖱️ 仮想キーボードの文字をクリックして入力
        - ⌫ 「削除」ボタンで最後の文字を削除
        - 📤 「送信」ボタンまたは直接入力フォームで推測を送信
        
        **🎨 色の意味:**
        - 🟩 **緑**: 正しい位置にある文字
        - 🟨 **黄**: 単語に含まれているが位置が違う文字
        - ⬜ **グレー**: 単語に含まれていない文字
        
        **💡 ヒント:**
        - よく使われる文字（E, A, R, I, O, T, N, S）から始めてみましょう
        - 母音と子音のバランスを考えて推測しましょう
        - 前の推測の結果を活用して次の推測を絞り込みましょう
        """)
    
    # フッター
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #9ca3af; font-size: 0.9rem;">Made with ❤️ using Streamlit | 楽しいWordleライフを！</p>',
        unsafe_allow_html=True
    )

def display_game_board():
    """ゲームボードを表示"""
    st.markdown("### 🎲 ゲームボード")
    
    # 過去の推測を表示
    for i in range(6):
        cols = st.columns(4)
        if i < len(st.session_state.guesses):
            guess, result = st.session_state.guesses[i]
            for j, (letter, status) in enumerate(zip(guess, result)):
                with cols[j]:
                    if status == 'correct':
                        st.markdown(f'''
                        <div style="
                            background: linear-gradient(135deg, #22c55e, #16a34a);
                            color: white;
                            text-align: center;
                            padding: 20px;
                            margin: 4px;
                            border-radius: 12px;
                            font-weight: bold;
                            font-size: 28px;
                            border: 3px solid #15803d;
                            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
                            transform: scale(1.05);
                        ">{letter}</div>
                        ''', unsafe_allow_html=True)
                    elif status == 'present':
                        st.markdown(f'''
                        <div style="
                            background: linear-gradient(135deg, #eab308, #ca8a04);
                            color: white;
                            text-align: center;
                            padding: 20px;
                            margin: 4px;
                            border-radius: 12px;
                            font-weight: bold;
                            font-size: 28px;
                            border: 3px solid #a16207;
                            box-shadow: 0 4px 12px rgba(234, 179, 8, 0.3);
                        ">{letter}</div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                        <div style="
                            background: linear-gradient(135deg, #6b7280, #4b5563);
                            color: white;
                            text-align: center;
                            padding: 20px;
                            margin: 4px;
                            border-radius: 12px;
                            font-weight: bold;
                            font-size: 28px;
                            border: 3px solid #374151;
                            box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
                        ">{letter}</div>
                        ''', unsafe_allow_html=True)
        elif i == len(st.session_state.guesses) and not st.session_state.game_over:
            # 現在の入力行
            current_letters = list(st.session_state.current_input) + [''] * (4 - len(st.session_state.current_input))
            for j, letter in enumerate(current_letters):
                with cols[j]:
                    if letter:
                        st.markdown(f'''
                        <div style="
                            background: linear-gradient(135deg, #3b82f6, #2563eb);
                            color: white;
                            text-align: center;
                            padding: 20px;
                            margin: 4px;
                            border-radius: 12px;
                            font-weight: bold;
                            font-size: 28px;
                            border: 3px solid #1d4ed8;
                            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                            animation: pulse 2s infinite;
                        ">{letter}</div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown('''
                        <div style="
                            background: rgba(248, 250, 252, 0.8);
                            border: 3px dashed #cbd5e1;
                            text-align: center;
                            padding: 20px;
                            margin: 4px;
                            border-radius: 12px;
                            font-size: 28px;
                            transition: all 0.3s ease;
                        ">&nbsp;</div>
                        ''', unsafe_allow_html=True)
        else:
            # 空の行
            for j in range(4):
                with cols[j]:
                    st.markdown('''
                    <div style="
                        background: rgba(248, 250, 252, 0.5);
                        border: 2px solid #e2e8f0;
                        text-align: center;
                        padding: 20px;
                        margin: 4px;
                        border-radius: 12px;
                        font-size: 28px;
                    ">&nbsp;</div>
                    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

