import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

# 한글 폰트 설정
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# 앱 제목
st.title("🛩️ 종이컵 비행기 실험 데이터 분석기")

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("📁 실험 데이터 엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    # 엑셀 데이터 읽기
    df = pd.read_excel(uploaded_file)

    st.subheader("🔍 원본 데이터 미리보기")
    st.dataframe(df)

    # 평균값 계산용 열
    group_col = "학생"
    feature_cols = ['I.D', 'O.D', 'H.W', 'R.B.T', 'R.B.S.L', 'W', 'L.H', 'L.A', 'F.P']

    # 평균값 계산
    df_avg = df.groupby(group_col)[feature_cols].mean().reset_index()

    st.subheader("📊 모둠별 평균값 (분석용 데이터)")
    st.dataframe(df_avg)

    # 입력(X), 목표(y) 정의
    X = df_avg.drop(columns=["F.P", group_col])
    y = df_avg["F.P"]

    # 학습/테스트 분할 및 모델 훈련
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 모델 성능 평가
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    st.success(f"✅ 모델 R² 점수: {r2:.2f}")

    # 변수 중요도 시각화
    st.subheader("📌 변수 중요도")
    importance_df = pd.DataFrame({
        "변수": X.columns,
        "중요도": model.feature_importances_
    }).sort_values(by="중요도", ascending=False)

    fig, ax = plt.subplots()
    sns.barplot(data=importance_df, x="중요도", y="변수", ax=ax)
    st.pyplot(fig)

    # 예측 입력 받기
    st.subheader("🧪 새 조건 입력 → 비행 성능 예측")

    input_data = {}
    for col in X.columns:
        input_data[col] = st.number_input(f"{col}", value=float(X[col].mean()))

    input_df = pd.DataFrame([input_data])
    predicted_fp = model.predict(input_df)[0]
    st.success(f"📈 예측된 비행 성능 (F.P): {predicted_fp:.2f}")

