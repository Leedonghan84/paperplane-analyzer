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

# 엑셀 템플릿 다운로드 버튼
if experiment in ["종이컵 비행기", "고리 비행기"]:
    file_name = f"{experiment}_샘플_양식.xlsx"
    towrite = generate_excel_with_two_sheets(experiment)
    st.download_button("📥 샘플 엑셀 양식 다운로드", data=towrite, file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("📂 실험 엑셀 업로드 (분석용 데이터 시트 포함)", type=["xlsx"])

if not uploaded_file:
    st.stop()

try:
    df = pd.read_excel(uploaded_file, sheet_name="분석용 데이터")
    df.columns = df.columns.str.replace("\n", " ").str.strip()
    df = df.select_dtypes(include=['number']).dropna()
except Exception:
    st.error("❌ '분석용 데이터' 시트를 불러오는 데 실패했습니다.")
    st.stop()

# 분석 시작
st.subheader("📊 분석 결과")
columns = df.columns.tolist()
target_candidates = [c for c in columns if '성능' in c or '평균' in c or c.lower() in ['target', 'y']]
default_target = target_candidates[0] if target_candidates else columns[-1]

target_col = st.selectbox("🎯 예측할 종속변수", columns, index=columns.index(default_target))
feature_cols = st.multiselect("🧪 독립변수(입력값)", [c for c in columns if c != target_col], default=[c for c in columns if c != target_col])

st.sidebar.subheader("🧠 모델 설정")
model_option = st.sidebar.selectbox("머신러닝 알고리즘 선택", ["선형회귀", "랜덤포레스트"])
tuning = st.sidebar.checkbox("튜닝 사용", value=(model_option == "랜덤포레스트"))
kfolds = st.sidebar.slider("K-Fold 수 (교차검증)", 2, 10, 5)

if model_option == "랜덤포레스트" and tuning:
    n_estimators = st.sidebar.slider("n_estimators", 10, 300, 100, 10)
    max_depth = st.sidebar.slider("max_depth", 1, 30, 5)
else:
    n_estimators = 100
    max_depth = None
X = df[feature_cols]
y = df[target_col]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = LinearRegression() if model_option == "선형회귀" else RandomForestRegressor(
    n_estimators=n_estimators, max_depth=max_depth, random_state=42
)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
mae = mean_absolute_error(y_test, y_pred)
cv_score = cross_val_score(model, X, y, cv=kfolds, scoring='r2').mean()

st.success(f"✅ 테스트 R²: {r2:.2f} | RMSE: {rmse:.2f} | MAE: {mae:.2f} | 교차검증 R² 평균: {cv_score:.2f}")

# 시각화: 예측 vs 실제
st.subheader("📈 예측 vs 실제")
fig1, ax1 = plt.subplots()
sns.regplot(x=model.predict(X), y=y, ax=ax1, ci=95, line_kws={"color": "blue"})
ax1.set_xlabel("예측값")
ax1.set_ylabel("실제값")
st.pyplot(fig1)

# 시각화: 독립변수별 관계
st.subheader("📉 독립변수별 성능 관계")
selected_feature = st.selectbox("🔍 분석할 변수 선택", feature_cols)
fig2, ax2 = plt.subplots()
sns.scatterplot(x=selected_feature, y=target_col, data=df, ax=ax2)
sns.regplot(x=selected_feature, y=target_col, data=df, ax=ax2, scatter=False, line_kws={"color": "red"})
st.pyplot(fig2)

# 변수 중요도
if model_option == "랜덤포레스트":
    st.subheader("📌 변수 중요도")
    importance_df = pd.DataFrame({"변수": X.columns, "중요도": model.feature_importances_}).sort_values(by="중요도", ascending=False)
    fig3, ax3 = plt.subplots()
    sns.barplot(data=importance_df, x="중요도", y="변수", ax=ax3)
    st.pyplot(fig3)

# 사용자 입력 예측
st.subheader("🧪 새 조건 입력 → 예측값")
input_data = {col: st.number_input(f"{col}", value=float(X[col].mean())) for col in feature_cols}
input_df = pd.DataFrame([input_data])
prediction = model.predict(input_df)[0]
st.success(f"📊 예측 결과: {prediction:.2f}")
