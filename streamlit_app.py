import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import io
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from openpyxl import Workbook

matplotlib.rcParams['font.family'] = 'NanumGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

st.title("✈️ 비행기 실험 데이터 분석기")

experiment = st.selectbox("🔬 실험 종류를 선택하세요", ["종이컵 비행기", "고리 비행기", "직접 업로드"])

# 샘플 엑셀 자동 생성 함수 (2시트 포함)
def generate_excel_with_two_sheets(experiment):
    wb = Workbook()
    ws_analysis = wb.active
    ws_analysis.title = "분석용 데이터"
    ws_input = wb.create_sheet("원본 데이터")

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
        ws_analysis.append(analysis_cols)
        for i in range(2, 102):
            row = []
            for col in analysis_cols:
                if col == "비행성능":
                    row.append(f"=AVERAGE('원본 데이터'!J{i}:N{i})")
                else:
                    col_index = input_cols.index(col)
                    col_letter = chr(65 + col_index)
                    row.append(f"='원본 데이터'!{col_letter}{i}")
            ws_analysis.append(row)
        ws_input.append(input_cols)

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
        ws_analysis.append(analysis_cols)
        for i in range(2, 102):
            row = []
            for col in analysis_cols:
                if col == "비행성능":
                    row.append(f"=AVERAGE('원본 데이터'!K{i}:O{i})")
                else:
                    col_index = input_cols.index(col)
                    col_letter = chr(65 + col_index)
                    row.append(f"='원본 데이터'!{col_letter}{i}")
            ws_analysis.append(row)
        ws_input.append(input_cols)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream

if experiment in ["종이컵 비행기", "고리 비행기"]:
    file_name = f"{experiment}_자동_양식.xlsx"
    towrite = generate_excel_with_two_sheets(experiment)
    st.download_button(
        label="📥 샘플 엑셀 양식 다운로드",
        data=towrite,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 파일 업로드 처리
if experiment == "종이컵 비행기":
    uploaded_file = st.file_uploader("📂 종이컵 비행기 엑셀 업로드 (분석용 데이터 시트)", type=["xlsx"], key="cup")
elif experiment == "고리 비행기":
    uploaded_file = st.file_uploader("📂 고리 비행기 엑셀 업로드 (분석용 데이터 시트)", type=["xlsx"], key="gori")
else:
    uploaded_file = st.file_uploader("📂 엑셀 파일 업로드 (자유 형식)", type=["xlsx"], key="custom")

# 데이터 처리
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="분석용 데이터")
    df.columns = df.columns.str.replace("\n", " ").str.strip()
    df = df.select_dtypes(include=['number']).dropna()
else:
    st.stop()

st.subheader("📋 데이터 미리보기")
st.dataframe(df)

# 종속/독립 변수 선택
columns = df.columns.tolist()
default_target = next((c for c in columns if '성능' in c or c.lower() in ['f.p', 'target', 'y', '평균값']), columns[-1])
target_col = st.selectbox("🎯 종속변수(예측할 값)", columns, index=columns.index(default_target))
feature_cols = st.multiselect("🧪 독립변수(입력값)", [c for c in columns if c != target_col], default=[c for c in columns if c != target_col])

# 모델 설정
st.sidebar.subheader("🧠 모델 설정")
model_option = st.sidebar.selectbox("머신러닝 알고리즘 선택", ["선형회귀", "랜덤포레스트"])
tuning = st.sidebar.checkbox("튜닝", value=(model_option == "랜덤포레스트"))

if model_option == "랜덤포레스트" and tuning:
    n_estimators = st.sidebar.slider("n_estimators", 10, 200, 100, 10)
    max_depth = st.sidebar.slider("max_depth", 1, 20, 5)
else:
    n_estimators = 100
    max_depth = None

# 학습
X = df[feature_cols]
y = df[target_col]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

if model_option == "선형회귀":
    model = LinearRegression()
else:
    model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
st.success(f"✅ 모델 R² 점수: {r2:.2f}")

# 예측 vs 실제
st.subheader("📈 실제값 vs 예측값")
full_pred = model.predict(X)
fig1, ax1 = plt.subplots()
sns.regplot(x=full_pred, y=y, ax=ax1, ci=95, line_kws={"color": "blue"})
ax1.set_xlabel("모델이 예측한 값")
ax1.set_ylabel(f"실제값 ({target_col})")
st.pyplot(fig1)

# 변수 중요도 (랜덤포레스트만)
if model_option == "랜덤포레스트":
    st.subheader("📌 변수 중요도")
    importance_df = pd.DataFrame({"변수": X.columns, "중요도": model.feature_importances_})
    importance_df = importance_df.sort_values(by="중요도", ascending=False)
    fig2, ax2 = plt.subplots()
    sns.barplot(data=importance_df, x="중요도", y="변수", ax=ax2)
    st.pyplot(fig2)

# 입력값 예측
st.subheader("🧪 새 조건 입력 → 예측값")
input_data = {}
for col in feature_cols:
    input_data[col] = st.number_input(col, value=float(X[col].mean()))
input_df = pd.DataFrame([input_data])
prediction = model.predict(input_df)[0]
st.success(f"📊 예측 결과: {prediction:.2f}")
