import streamlit as st
from PIL import Image
import pytesseract
import re
from datetime import datetime, timedelta
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from holidays_data import JAPANESE_HOLIDAYS, HOLIDAY_KEYWORDS
from pdf2image import convert_from_bytes
import io

# Google Calendar API設定
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CLIENT_SECRETS_FILE = "credentials.json"

# 学年・学科データ構造
DEPARTMENTS = {
    "海事": ["海事学科"],
    "海洋": ["海洋学科"],
    "流通": ["流通学科"]
}

SPECIALIZATIONS = {
    "海洋": {
        "3年": ["制御", "機関"],
        "4年": ["制御", "機関"]
    }
}

def get_user_profile():
    """
    ユーザーの学年・学科・専攻情報を取得
    """
    st.sidebar.header("👤 学生情報")
    
    # 学年選択
    grade = st.sidebar.selectbox(
        "学年を選択してください",
        ["1年", "2年", "3年", "4年"],
        key="grade_select"
    )
    
    # 学科選択
    department = st.sidebar.selectbox(
        "学科を選択してください",
        ["海事", "海洋", "流通"],
        key="department_select"
    )
    
    # 専攻選択（海洋学科の3・4年生のみ）
    specialization = None
    if department == "海洋" and grade in ["3年", "4年"]:
        specialization = st.sidebar.selectbox(
            "専攻を選択してください",
            ["制御", "機関"],
            key="specialization_select"
        )
    
    return {
        "grade": grade,
        "department": department,
        "specialization": specialization
    }

def is_holiday_event(title, date_str):
    """
    予定が祝日関連かどうかを判定する
    """
    # 祝日キーワードが含まれているかチェック
    title_lower = title.lower()
    for keyword in HOLIDAY_KEYWORDS:
        if keyword in title or keyword.lower() in title_lower:
            return True
    
    # 日付が祝日かどうかをチェック
    try:
        # 日付文字列から年を抽出
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                year = parts[0]
                month = parts[1].zfill(2)
                day = parts[2].zfill(2)
                date_key = f"{month}月{day}日"
                
                if year in JAPANESE_HOLIDAYS and date_key in JAPANESE_HOLIDAYS[year]:
                    return True
    except:
        pass
    
    return False

def filter_schedules_by_profile(schedules, user_profile):
    """
    ユーザープロファイルに基づいて予定をフィルタリング
    """
    filtered_schedules = []
    
    for schedule in schedules:
        # 祝日関連の予定をスキップ
        if is_holiday_event(schedule["title"], schedule["date"]):
            continue
        
        # 基本的にすべての予定を含める
        include_schedule = True
        
        # 学科固有の予定をチェック        title_lower = schedule["title"].lower()
        # 学科名が含まれている場合のフィルタリング
        if any(dept in schedule["title"] for dept in ["海事", "海洋", "流通"]):
            if user_profile["department"] not in schedule["title"]:
                include_schedule = False
        
        # 専攻固有の予定をチェック（海洋学科の3・4年        if user_profile["specialization"] and any(spec in schedule["title"] for spec in ["制御", "機関"]):                include_schedule = False
        
        # 学年固有の予定をチェック
        if any(grade in schedule[\'title\'] for grade in ["1年", "2年", "3年", "4年"]):
            if user_profile[\'grade\'] not in schedule[\'title\']:
                include_schedule = False
        
        if include_schedule:
            # ユーザー情報を予定に追加
            schedule_copy = schedule.copy()
            schedule_copy[\'target_profile\'] = user_profile
            filtered_schedules.append(schedule_copy)
    
    return filtered_schedules

def extract_schedule_info(text, user_profile):
    """
    抽出されたテキストから予定情報を解析し、ユーザープロファイルでフィルタリング
    """
    schedules = []
    lines = text.split(\'\\n\')
    
    # 日付パターン（例：12/25、2024/12/25、12月25日など）
    date_patterns = [
        r\'(\\d{1,2})/(\\d{1,2})\',
        r\'(\\d{4})/(\\d{1,2})/(\\d{1,2})\',
        r\'(\\d{1,2})月(\\d{1,2})日\',
        r\'(\\d{4})年(\\d{1,2})月(\\d{1,2})日\'
    ]
    
    # 時刻パターン（例：10:00、午前10時、10時など）
    time_patterns = [
        r\'(\\d{1,2}):(\\d{2})\',
        r\'午前(\\d{1,2})時\',
        r\'午後(\\d{1,2})時\',
        r\'(\\d{1,2})時\'
    ]
    
    current_date = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 日付を検索
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match:
                if len(match.groups()) == 2:  # MM/DD or MM月DD日
                    month, day = match.groups()
                    current_date = f"2024/{month.zfill(2)}/{day.zfill(2)}"
                elif len(match.groups()) == 3:  # YYYY/MM/DD or YYYY年MM月DD日
                    year, month, day = match.groups()
                    current_date = f"{year}/{month.zfill(2)}/{day.zfill(2)}"
                break
        
        # 時刻と予定内容を検索
        for pattern in time_patterns:
            match = re.search(pattern, line)
            if match:
                if pattern == r\'(\\d{1,2}):(\\d{2})\':
                    hour, minute = match.groups()
                    time_str = f"{hour.zfill(2)}:{minute}"
                elif pattern == r\'午前(\\d{1,2})時\':
                    hour = match.groups()[0]
                    time_str = f"{hour.zfill(2)}:00"
                elif pattern == r\'午後(\\d{1,2})時\':
                    hour = str(int(match.groups()[0]) + 12)
                    time_str = f"{hour.zfill(2)}:00"
                else:  # (\\d{1,2})時
                    hour = match.groups()[0]
                    time_str = f"{hour.zfill(2)}:00"
                
                # 予定内容を抽出（時刻以降のテキスト）
                title = re.sub(r\'(\\d{1,2}):(\\d{2})|午前(\\d{1,2})時|午後(\\d{1,2})時|(\\d{1,2})時\', \'\', line).strip()
                title = re.sub(r\'[^\\w\\s]\', \'\', title).strip()  # 特殊文字を除去
                
                if current_date and title:
                    schedules.append({
                        \'date\': current_date,
                        \'time\': time_str,
                        \'title\': title,
                        \'datetime\': f"{current_date} {time_str}"
                    })
                break
    
    # ユーザープロファイルに基づいてフィルタリング
    filtered_schedules = filter_schedules_by_profile(schedules, user_profile)
    
    return filtered_schedules

def create_google_calendar_event(service, schedule):
    """
    Google Calendarにイベントを作成する
    """
    try:
        # 日時をISO形式に変換
        start_datetime = datetime.strptime(schedule[\'datetime\'], \'%Y/%m/%d %H:%M\')
        end_datetime = start_datetime + timedelta(hours=1)  # デフォルトで1時間のイベント
        
        # ユーザー情報を説明に追加
        description = ""
        if \'target_profile\' in schedule:
            profile = schedule[\'target_profile\']
            description = f"対象: {profile[\'grade\']} {profile[\'department\']}学科"
            if profile[\'specialization\']:
                description += f" {profile[\'specialization\']}専攻"
        
        event = {
            \'summary\': schedule[\'title\'],
            \'description\': description,
            \'start\': {
                \'dateTime\': start_datetime.isoformat(),
                \'timeZone\': \'Asia/Tokyo\',
            },
            \'end\': {
                \'dateTime\': end_datetime.isoformat(),
                \'timeZone\': \'Asia/Tokyo\',
            },
        }
        
        event = service.events().insert(calendarId=\'primary\', body=event).execute()
        return event
    except Exception as e:
        st.error(f"イベント作成エラー: {str(e)}")
        return None

def get_google_calendar_service():
    """
    Google Calendar APIサービスを取得する
    """
    creds = None
    
    # トークンファイルが存在する場合は読み込み
    if os.path.exists(\'token.json\'):
        creds = Credentials.from_authorized_user_file(\'token.json\', SCOPES)
    
    # 認証が無効または存在しない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            return None
    
    # トークンを保存
    with open(\'token.json\', \'w\') as token:
        token.write(creds.to_json())
    
    return build(\'calendar\', \'v3\', credentials=creds)

# Streamlit UI
st.set_page_config(page_title="海洋工学部予定追加アプリ", layout="wide")

st.title("📅 海洋工学部予定追加アプリ")
st.markdown("---")

# ユーザープロファイル取得
user_profile = get_user_profile()

# サイドバーでGoogle Calendar認証状態を表示
with st.sidebar:
    st.markdown("---")
    st.header("🔐 Google Calendar認証")
    
    if not os.path.exists(\'credentials.json\'):
        st.error("credentials.jsonファイルが見つかりません。")
        st.write("Google Cloud Consoleで作成したOAuth 2.0認証情報ファイルを\'credentials.json\'として保存してください。")
        st.write("[Google Cloud Console](https://console.cloud.google.com/)")
    else:
        if os.path.exists(\'token.json\'):
            st.success("✅ 認証済み")
            if st.button("認証をリセット"):
                os.remove(\'token.json\')
                st.rerun()
        else:
            st.warning("⚠️ 未認証")
            st.write("Googleカレンダーとの連携には認証が必要です。")

# ユーザー情報表示
st.info(f"👤 **選択中**: {user_profile[\'grade\']} {user_profile[\'department\']}学科" + \
        (f" {user_profile[\'specialization\']}専攻" if user_profile[\'specialization\'] else ""))

# メインコンテンツ
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📷 画像アップロード")
    uploaded_file = st.file_uploader(
        "予定表の画像またはPDFを選択してください", 
        type=["png", "jpg", "jpeg", "pdf"],
        help="JPG、PNG、PDF形式のファイルをアップロードできます"
    )
    
    if uploaded_file is not None:
        file_type = uploaded_file.type
        
        if file_type == "application/pdf":
            # PDFを画像に変換
            images = convert_from_bytes(uploaded_file.read(), first_page=1, last_page=1)
            if images:
                image = images[0] # 最初のページのみ処理
                st.image(image, caption=\'アップロードされたPDFの1ページ目\', use_column_width=True)
            else:
                st.error(\'PDFから画像を抽出できませんでした。\')
                image = None
        elif file_type in ["image/png", "image/jpeg"]:
            image = Image.open(uploaded_file)
            st.image(image, caption=\'アップロードされた画像\', use_column_width=True)
        else:
            st.error("サポートされていないファイル形式です。PNG, JPG, JPEG, PDFファイルをアップロードしてください。")
            image = None

with col2:
    st.header("📝 テキスト抽出・予定解析")
    
    if uploaded_file is not None:
        with st.spinner("画像からテキストを抽出中..."):
            # OCRでテキストを抽出
            extracted_text = pytesseract.image_to_string(image, lang=\'jpn+eng\')
        
        with st.expander("抽出されたテキストを表示"):
            st.text_area("", extracted_text, height=200)
        
        # 予定情報を解析（ユーザープロファイルでフィルタリング）
        schedules = extract_schedule_info(extracted_text, user_profile)
        
        if schedules:
            st.success(f"✅ あなたに関連する{len(schedules)}件の予定を検出しました")
            
            # 検出された予定を表示
            for i, schedule in enumerate(schedules):
                with st.container():
                    st.write(f"**予定 {i+1}:**")
                    st.write(f"📅 日付: {schedule[\'date\']}")
                    st.write(f"🕐 時刻: {schedule[\'time\']}")
                    st.write(f"📋 内容: {schedule[\'title\']}")
                    if \'target_profile\' in schedule:
                        profile = schedule[\'target_profile\']
                        st.write(f"🎯 対象: {profile[\'grade\']} {profile[\'department\']}学科" + \
                                (f" {profile[\'specialization\']}専攻" if profile[\'specialization\'] else ""))
                    st.write("---")
        else:
            st.warning("⚠️ あなたに関連する予定情報を検出できませんでした")
            st.write("画像の品質を確認するか、手動で予定を入力してください。")
# Google Calendarへの追加セクション
if uploaded_file is not None and \'schedules\' in locals() and schedules:
    st.header("📤 Googleカレンダーへの追加")
    
    if not os.path.exists(\'credentials.json\'):
        st.error("Google Calendar APIの認証設定が必要です。")
        st.write("1. [Google Cloud Console](https://console.cloud.google.com/)")
        st.write("2. Calendar APIを有効化")
        st.write("3. OAuth 2.0認証情報を作成し、credentials.jsonとして保存")
    elif not os.path.exists(\'token.json\'):
        st.warning("Googleアカウントでの認証が必要です。")
        st.write("認証用のリンクを生成するには、credentials.jsonファイルが正しく設定されている必要があります。")
    else:
        service = get_google_calendar_service()
        if service:
            if st.button("🚀 関連する予定をGoogleカレンダーに追加", type="primary"):
                success_count = 0
                with st.spinner(\'Googleカレンダーに予定を追加中...\'):
                    for schedule in schedules:
                        event = create_google_calendar_event(service, schedule)
                        if event:
                            success_count += 1
                
                if success_count > 0:
                    st.success(f"✅ {success_count}件の予定をGoogleカレンダーに追加しました！")
                else:
                    st.error("❌ 予定の追加に失敗しました。")

# フッター
st.markdown("---")
st.markdown("💡 **使い方のヒント:**")
st.markdown("- 左側のサイドバーで学年・学科・専攻を選択してください")
st.markdown("- 画像は文字がはっきりと読める高解像度のものを使用してください")
st.markdown("- 学科名や学年が含まれた予定は自動的にフィルタリングされます")
st.markdown("- 初回利用時はGoogle Calendar APIの認証設定が必要です")



