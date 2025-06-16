import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

st.title("🛩️ 종이컵 비행기 실험 데이터 분석기")

uploaded_file = st.file_uploader("📁 실험 원본 데이터 엑셀파일을 업로드하세요 (5회 반복 측정 포함)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("🧾 원본 데이터 미리보기")
    st.dataframe(df)

    # ▶️ 열 이름 예시: 학생, 실험번호, I.D, O.D, ..., F.P
    group_cols = ["학생"]
    feature_cols = ['I.D', 'O.D', 'H.W', 'R.B.T', 'R.B.S.L', 'W', 'L.H', 'L.A', 'F.P']

    # 평균값 계산
    df_avg = df.groupby("학생")[feature_cols].mean().reset_index()

    st.subheader("📊 학생별 평균값 (분석용 데이터)")
    st.dataframe(df_avg)

    X = df_avg.drop(columns=["F.P", "학생"])
    y = df_avg["F.P"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    score = r2_score(y_test, y_pred)
    st.success(f"모델 R² 점수: {score:.2f}")

    # 중요도 시각화
    st.subheader("🌟 변수 중요도")
    importances = model.feature_importances_
    importance_df = pd.DataFrame({
        "변수": X.columns,
        "중요도": importances
    }).sort_values(by="중요도", ascending=False)

    fig1, ax1 = plt.subplots()
    sns.barplot(data=importance_df, x="중요도", y="변수", ax=ax1)
    st.pyplot(fig1)

    # 예측 입력폼
    st.subheader("🧪 새 조건 입력 → 비행성능 예측")

    input_data = {}
    for col in X.columns:
        input_data[col] = st.number_input(f"{col}", value=float(X[col].mean()))

    input_df = pd.DataFrame([input_data])
    prediction = model.predict(input_df)[0]
    st.success(f"예측된 비행성능: {prediction:.2f}")
