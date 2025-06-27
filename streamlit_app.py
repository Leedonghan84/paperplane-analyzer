import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import matplotlib
import io
import os
import re

from openpyxl import Workbook
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# 한글 폰트 설정
font_path = "./NanumGothic.ttf"
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    font_name = fm.FontProperties(fname=font_path).get_name()
    plt.rcParams['font.family'] = font_name
    matplotlib.rcParams['font.family'] = font_name
    st.markdown(f"✅ 폰트 설정됨: `{font_name}`")
else:
    st.warning("⚠️ NanumGothic.ttf 파일이 없어 기본 폰트로 설정됩니다.")
    matplotlib.rcParams['font.family'] = ['Malgun Gothic', 'AppleGothic', 'Arial']

matplotlib.rcParams['axes.unicode_minus'] = False

# 잘못된 문자 제거 함수

def remove_illegal_characters(s):
    if isinstance(s, str):
        return re.sub(r'[\x00-\x1F]', '', s)
    return s

st.title("✈️ 비행기 실험 데이터 분석기")

experiment = st.selectbox("🔬 실험 종류를 선택하세요", ["종이컵 비행기", "고리 비행기", "직접 업로드"])

# 데이터 시트 생성

def generate_excel_with_two_sheets(experiment):
    wb = Workbook()
    ws_analysis = wb.active
    ws_analysis.title = remove_illegal_characters("분석용 데이터")
    ws_input = wb.create_sheet(remove_illegal_characters("원본 데이터"))

    if experiment == "종이컵 비행기":
        input_cols = [
            "번호", "모둠명", "안쪽 지름(cm)", "바깥쪽 지름(cm)", "반너비(cm)", "고무줄 감은 횟수",
            "고무줄 늘어난 길이(cm)", "무게(g)", "날리는 높이(cm)",
            "비행성능1", "비행성능2", "비행성능3", "비행성능4", "비행성능5"
        ]
        analysis_cols = [
            "안쪽 지름(cm)", "바깥쪽 지름(cm)", "반너비(cm)", "고무줄 감은 횟수",
            "고무줄 늘어난 길이(cm)", "무게(g)", "날리는 높이(cm)", "비행성능"
        ]
        ws_analysis.append([remove_illegal_characters(c) for c in analysis_cols])
        for i in range(2, 102):
            row = []
            for col in analysis_cols:
                if col == "비행성능":
                    row.append(f"=AVERAGE('원본 데이터'!J{i}:N{i})")
                else:
                    col_index = input_cols.index(col)
                    col_letter = chr(65 + col_index)
                    row.append(f"='원본 데이터'!{col_letter}{i}")
            ws_analysis.append([remove_illegal_characters(c) for c in row])
        ws_input.append([remove_illegal_characters(c) for c in input_cols])

    elif experiment == "고리 비행기":
        input_cols = [
            "번호", "모둠명", "앞 쪽 고리 지름(cm)", "앞 쪽 고리 두께(cm)",
            "뒤 쪽 고리 지름(cm)", "뒤 쪽 고리 두께(cm)",
            "질량(g)", "고무줄길이(cm)", "무게 중심(cm)", "고무줄늘어난길이(cm)",
            "비행성능1", "비행성능2", "비행성능3", "비행성능4", "비행성능5"
        ]
        analysis_cols = [
            "앞 쪽 고리 지름(cm)", "앞 쪽 고리 두께(cm)", "뒤 쪽 고리 지름(cm)", "뒤 쪽 고리 두께(cm)",
            "질량(g)", "고무줄늘어난길이(cm)", "비행성능"
        ]
        ws_analysis.append([remove_illegal_characters(c) for c in analysis_cols])
        for i in range(2, 102):
            row = []
            for col in analysis_cols:
                if col == "비행성능":
                    row.append(f"=AVERAGE('원본 데이터'!K{i}:O{i})")
                else:
                    col_index = input_cols.index(col)
                    col_letter = chr(65 + col_index)
                    row.append(f"='원본 데이터'!{col_letter}{i}")
            ws_analysis.append([remove_illegal_characters(c) for c in row])
        ws_input.append([remove_illegal_characters(c) for c in input_cols])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream
