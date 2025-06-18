import streamlit as st
import pytesseract
from PIL import Image
import jpholiday
import datetime
import re

st.set_page_config(page_title="海洋工学部行事予定追加アプリ")

st.title("海洋工学部行事予定追加アプリ")

# 画像アップロード
uploaded_file = st.file_uploader("予定表画像をアップロード", type=["jpg", "jpeg", "png", "bmp"])

# 学年・学科・専攻・試験区分の選択
grade = st.selectbox("学年", ["", "1年", "2年", "3年", "4年"])
course = st.selectbox("学科", ["", "海事", "海洋", "流通"])
subcourse = ""
if grade in ["3年", "4年"] and course == "海洋":
    subcourse = st.selectbox("専攻", ["", "制御", "機関"])
exam_type = st.selectbox("試験区分", ["", "S試験（セメスター）", "Q試験（クォーター）"])

def parse_events(text, selected_grade, selected_course, selected_subcourse=None, selected_exam_type=None):
    pattern = r"(\d{1,2}/\d{1,2})\s*(\d+年)?\s*(海事|海洋|流通)?\s*(制御|機関)?\s*(S試験|Q試験)?\s*(.+)"
    events = []
    year = datetime.datetime.now().year
    for line in text.split("\n"):
        m = re.match(pattern, line)
        if m:
            month_day, grade, course, subcourse, exam_type, title = m.groups()
            grade = grade or ""
            course = course or ""
            subcourse = subcourse or ""
            exam_type = exam_type or ""
            if (
                (not selected_grade or selected_grade in grade)
                and (not selected_course or selected_course in course)
                and (
                    not selected_subcourse
                    or selected_subcourse in subcourse
                )
                and (
                    not selected_exam_type
                    or (selected_exam_type.startswith("S試験") and "S試験" in exam_type)
                    or (selected_exam_type.startswith("Q試験") and "Q試験" in exam_type)
                )
            ):
                try:
                    date = datetime.datetime.strptime(f"{year}/{month_day}", "%Y/%m/%d")
                    events.append({"date": date, "title": title})
                except ValueError:
                    continue
    return events

def filter_holidays(events):
    return [e for e in events if not jpholiday.is_holiday(e["date"])]

if uploaded_file and grade and course and exam_type:
    st.write("OCRおよび予定抽出中...")
    image = Image.open(uploaded_file)
    text = pytesseract.image_to_string(image, lang="jpn")
    events = parse_events(text, grade, course, subcourse, "S試験" if exam_type.startswith("S") else "Q試験")
    events = filter_holidays(events)

    if events:
        st.success("抽出された予定リスト：")
        for e in events:
            st.write(f"{e['date'].strftime('%Y-%m-%d')} {e['title']}")
        st.info("Googleカレンダーに追加機能はローカルPython環境でのみ動作します。")
        st.write("カレンダー自動追加にはGoogle API認証情報が必要なため、Streamlit Cloudなどの共有環境ではセキュリティ上、自動連携は推奨されません。")
    else:
        st.warning("該当する予定がありませんでした。")
else:
    st.info("画像、学年、学科、試験区分をすべて選択してください。")

st.markdown("---")
st.caption("© 海洋工学部行事予定追加アプリ")