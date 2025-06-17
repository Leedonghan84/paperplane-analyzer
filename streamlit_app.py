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

st.title("🛩️ 종이컵 비행기 실험 평균값 분석기")

uploaded_file = st.file_uploader("📁 평균값 엑셀 파일 업로드 (모둠별 1줄씩)", type=["xlsx"])

if uploaded_file:
    try:
        # 데이터 불러오기
        df = pd.read_excel(uploaded_file)
        st.subheader("📋 업로드된 평균 데이터")
        st.dataframe(df)

        # 분석 대상 열만 추출
        feature_cols = ['I.D', 'O.D', 'H.W', 'R.B.T', 'R.B.S.L', 'W', 'L.H', 'L.A', 'F.P']
        df = df[feature_cols]

        # 결측치 제거
        df = df.dropna()

        # X, y 분리
        X = df.drop(columns=["F.P"])
        y = df["F.P"]

        # 모델 학습
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # 예측 성능
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        st.success(f"✅ 모델 R² 점수: {r2:.2f}")

        # 중요도 시각화
        st.subheader("📌 변수 중요도")
        importance_df = pd.DataFrame({
            "변수": X.columns,
            "중요도": model.feature_importances_
        }).sort_values(by="중요도", ascending=False)

        fig, ax = plt.subplots()
        sns.barplot(data=importance_df, x="중요도", y="변수", ax=ax)
        st.pyplot(fig)

        # 새 예측 입력
        st.subheader("🧪 새 조건 입력 → 비행성능 예측")
        input_data = {}
        for col in X.columns:
            input_data[col] = st.number_input(f"{col}", value=float(X[col].mean()))
        input_df = pd.DataFrame([input_data])
        prediction = model.predict(input_df)[0]
        st.success(f"📈 예측된 비행 성능 (F.P): {prediction:.2f}")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
