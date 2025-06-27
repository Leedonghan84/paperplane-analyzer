import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import matplotlib.font_manager as fm
import os
from openpyxl import Workbook
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from io import BytesIO

# ✅ 한글 폰트 설정
FONT_PATH = "./NanumGothic.ttf"
if os.path.exists(FONT_PATH):
    font_name = fm.FontProperties(fname=FONT_PATH).get_name()
    matplotlib.rc('font', family=font_name)
else:
    st.warning("⚠️ NanumGothic.ttf 파일이 없어 기본 폰트로 설정됩니다.")
    matplotlib.rcParams['font.family'] = ['Malgun Gothic', 'AppleGothic', 'Arial']
matplotlib.rcParams['axes.unicode_minus'] = False

st.title("✈️ 비행기 실험 데이터 분석기")

# 📁 샘플 엑셀 생성
def generate_excel(experiment):
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "분석용 데이터"
    ws2 = wb.create_sheet("원본 데이터")

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
        ws1.append(analysis_cols)
        for i in range(2, 102):
            row = []
            for col in analysis_cols:
                if col == "비행성능":
                    row.append(f"=AVERAGE('원본 데이터'!J{i}:N{i})")
                else:
                    idx = input_cols.index(col)
                    letter = chr(65 + idx)
                    row.append(f"='원본 데이터'!{letter}{i}")
            ws1.append(row)
        ws2.append(input_cols)

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
        ws1.append(analysis_cols)
        for i in range(2, 102):
            row = []
            for col in analysis_cols:
                if col == "비행성능":
                    row.append(f"=AVERAGE('원본 데이터'!K{i}:O{i})")
                else:
                    idx = input_cols.index(col)
                    letter = chr(65 + idx)
                    row.append(f"='원본 데이터'!{letter}{i}")
            ws1.append(row)
        ws2.append(input_cols)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# 실험 선택 및 샘플 양식 다운로드
experiment = st.selectbox("🔬 실험 종류 선택", ["종이컵 비행기", "고리 비행기", "직접 업로드"])
if experiment != "직접 업로드":
    st.download_button(
        label="📥 샘플 엑셀 양식 다운로드",
        data=generate_excel(experiment),
        file_name=f"{experiment}_양식.xlsx"
    )

# 📂 데이터 업로드
uploaded = st.file_uploader("📂 '분석용 데이터' 시트가 포함된 엑셀 업로드", type="xlsx")
if not uploaded:
    st.stop()

try:
    df = pd.read_excel(uploaded, sheet_name="분석용 데이터")
except:
    st.error("❌ '분석용 데이터' 시트를 찾을 수 없습니다.")
    st.stop()

df.columns = df.columns.str.replace("\n", " ").str.strip()
df = df.select_dtypes(include='number').dropna()

st.subheader("📋 데이터 미리보기")
st.dataframe(df)

# 변수 선택
columns = df.columns.tolist()
target_col = st.selectbox("🎯 종속변수", columns, index=len(columns)-1)
feature_cols = st.multiselect("🧪 독립변수", [c for c in columns if c != target_col], default=[c for c in columns if c != target_col])

X, y = df[feature_cols], df[target_col]

# 🧠 모델 설정
st.sidebar.subheader("모델 설정")
model_type = st.sidebar.selectbox("모델 선택", ["선형회귀", "랜덤포레스트"])
use_tuning = st.sidebar.checkbox("튜닝 사용", value=(model_type == "랜덤포레스트"))
kfold = st.sidebar.slider("K-Fold 수", 2, 10, 5)

if model_type == "랜덤포레스트" and use_tuning:
    n_estimators = st.sidebar.slider("n_estimators", 10, 200, 100, 10)
    max_depth = st.sidebar.slider("max_depth", 1, 30, 10)
else:
    n_estimators = 100
    max_depth = None

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

if model_type == "선형회귀":
    model = LinearRegression()
else:
    model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
cv_r2 = cross_val_score(model, X, y, cv=kfold, scoring='r2').mean()

st.success(f"✅ 테스트셋 R²: {r2:.2f} | RMSE: {rmse:.2f} | MAE: {mae:.2f} | 교차검증 R² 평균: {cv_r2:.2f}")

# 📈 예측 vs 실제
st.subheader("📈 예측 vs 실제")
fig1, ax1 = plt.subplots()
sns.regplot(x=model.predict(X), y=y, ax=ax1, line_kws={"color": "blue"})
ax1.set_xlabel("예측값")
ax1.set_ylabel("실제값")
st.pyplot(fig1)

# 📉 변수별 관계
st.subheader("📉 독립변수별 관계")
selected_feature = st.selectbox("변수 선택", feature_cols)
fig2, ax2 = plt.subplots()
sns.scatterplot(data=df, x=selected_feature, y=target_col, ax=ax2)
sns.regplot(data=df, x=selected_feature, y=target_col, ax=ax2, scatter=False, line_kws={"color": "red"})
st.pyplot(fig2)

# 📌 변수 중요도
if model_type == "랜덤포레스트":
    st.subheader("📌 변수 중요도")
    imp = pd.DataFrame({"변수": feature_cols, "중요도": model.feature_importances_}).sort_values("중요도", ascending=False)
    fig3, ax3 = plt.subplots()
    sns.barplot(data=imp, y="변수", x="중요도", ax=ax3)
    st.pyplot(fig3)

# 🧪 새 조건 입력 예측
st.subheader("🧪 새 입력값 예측")
user_input = {col: st.number_input(col, value=float(df[col].mean())) for col in feature_cols}
pred = model.predict(pd.DataFrame([user_input]))[0]
st.success(f"📊 예측값: {pred:.2f}")
