import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# ✅ 한글 깨짐 방지용 폰트 설정
matplotlib.rcParams['font.family'] = 'NanumGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

st.title("🛩️ 종이컵 비행기 실험 데이터 분석기")

uploaded_file = st.file_uploader("📁 평균값 엑셀파일 업로드 (1줄씩 모둠별 평균 데이터)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.subheader("📋 업로드된 데이터 미리보기")
        st.dataframe(df)

        feature_cols = ['I.D', 'O.D', 'H.W', 'R.B.T', 'R.B.S.L', 'W', 'L.H', 'L.A']
        target_col = 'F.P'

        df = df[feature_cols + [target_col]].dropna()
        X, y = df[feature_cols], df[target_col]

        st.sidebar.subheader("🧠 모델 설정")
        model_option = st.sidebar.selectbox("머신러닝 알고리즘 선택", ["선형회귀", "랜덤포레스트"])
        tuning = st.sidebar.checkbox("튜닝", value=(model_option == "랜덤포레스트"))

        # 튜닝 옵션
        if model_option == "랜덤포레스트" and tuning:
            n_estimators = st.sidebar.slider("n_estimators", 10, 200, 100, 10)
            max_depth = st.sidebar.slider("max_depth", 1, 20, 5)
        else:
            n_estimators = 100
            max_depth = None

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        if model_option == "선형회귀":
            model = LinearRegression()
        else:
            model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        st.success(f"✅ 모델 R² 점수: {r2:.2f}")

        # 📈 실제값 vs 예측값 그래프
        st.subheader("📈 실제값 vs 예측값")
        full_pred = model.predict(X)
        fig1, ax1 = plt.subplots()
        sns.regplot(x=full_pred, y=y, ax=ax1, ci=95, line_kws={"color": "blue"})
        ax1.set_xlabel("모델이 예측한 값")
        ax1.set_ylabel("실제 비행성능 (F.P)")
        st.pyplot(fig1)

        # 📌 변수 중요도 (랜덤포레스트만)
        if model_option == "랜덤포레스트":
            st.subheader("📌 변수 중요도")
            importance_df = pd.DataFrame({
                "변수": X.columns,
                "중요도": model.feature_importances_
            }).sort_values(by="중요도", ascending=False)
            fig2, ax2 = plt.subplots()
            sns.barplot(data=importance_df, x="중요도", y="변수", ax=ax2)
            st.pyplot(fig2)

        # 📉 선택 변수와 F.P 관계
        st.subheader("📉 독립변수 vs 비행성능 (F.P)")
        selected_feature = st.selectbox("변수를 선택하세요", feature_cols)
        fig3, ax3 = plt.subplots()
        sns.regplot(data=df, x=selected_feature, y="F.P", ax=ax3,
                    scatter_kws={"alpha": 0.6}, line_kws={"color": "red"})
        ax3.set_xlabel(selected_feature)
        ax3.set_ylabel("비행성능 (F.P)")
        st.pyplot(fig3)
        corr = df[selected_feature].corr(df["F.P"])
        st.caption(f"📈 상관계수 (Pearson r): {corr:.2f}")

        # 🧪 예측 입력
        st.subheader("🧪 새 조건 입력 → 비행성능 예측")
        input_data = {}
        for col in feature_cols:
            input_data[col] = st.number_input(col, value=float(X[col].mean()))
        input_df = pd.DataFrame([input_data])
        prediction = model.predict(input_df)[0]
        st.success(f"📈 예측된 비행성능 (F.P): {prediction:.2f}")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
