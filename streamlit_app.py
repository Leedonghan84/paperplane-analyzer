import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

# ✅ 한글 폰트 설정 (Windows용)
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

st.title("🛩️ 종이컵 비행기 실험 분석 웹앱")

# 📁 엑셀 업로드
uploaded_file = st.file_uploader("엑셀파일 업로드 (반복 측정 포함된 원본 데이터)", type=["xlsx"])

if uploaded_file:
    try:
        # 데이터 불러오기
        df = pd.read_excel(uploaded_file)
        st.subheader("📋 원본 데이터 미리보기")
        st.dataframe(df)

        # 분석에 필요한 열 지정
        group_col = "학생"
        feature_cols = ['I.D', 'O.D', 'H.W', 'R.B.T', 'R.B.S.L', 'W', 'L.H', 'L.A', 'F.P']

        # 평균값 계산
        df_avg = df.groupby(group_col)[feature_cols].mean().reset_index()

        # ⚠️ NaN 제거 + 숫자만 필터
        df_avg = df_avg.dropna()
        df_avg = df_avg[df_avg["F.P"].apply(lambda x: isinstance(x, (int, float)))]

        st.subheader("📊 분석용 평균 데이터")
        st.dataframe(df_avg)

        # X, y 분리
        X = df_avg.drop(columns=["F.P", group_col])
        y = df_avg["F.P"]

        # 학습
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # 평가
        y_pred = model.predict(X_test)
        score = r2_score(y_test, y_pred)
        st.success(f"✅ 모델 R² 점수: {score:.2f}")

        # 중요도 시각화
        st.subheader("🌟 변수 중요도")
        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            "변수": X.columns,
            "중요도": importances
        }).sort_values(by="중요도", ascending=False)

        fig, ax = plt.subplots()
        sns.barplot(data=importance_df, x="중요도", y="변수", ax=ax)
        st.pyplot(fig)

        # 예측 입력
        st.subheader("✏️ 새 조건 입력 → 비행성능 예측")
        input_data = {}
        for col in X.columns:
            input_data[col] = st.number_input(f"{col}", value=float(X[col].mean()))
        input_df = pd.DataFrame([input_data])
        prediction = model.predict(input_df)[0]
        st.success(f"🚀 예측된 비행성능 (F.P): {prediction:.2f}")

    except Exception as e:
        st.error(f"오류 발생: {e}")
