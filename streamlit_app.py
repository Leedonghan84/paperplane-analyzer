import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# ✅ 한글 깨짐 방지용 폰트 설정 (NanumGothic 사용)
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

        # 데이터 정제
        df = df[feature_cols + [target_col]]
        df = df.dropna()

        # X, y 분리
        X = df[feature_cols]
        y = df[target_col]

        # 모델 학습
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # 예측 성능 평가
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        st.success(f"✅ 모델 R² 점수: {r2:.2f}")

        # 🔹 변수 중요도
        st.subheader("📌 변수 중요도")
        importance_df = pd.DataFrame({
            "변수": X.columns,
            "중요도": model.feature_importances_
        }).sort_values(by="중요도", ascending=False)
        fig1, ax1 = plt.subplots()
        sns.barplot(data=importance_df, x="중요도", y="변수", ax=ax1)
        st.pyplot(fig1)

        # 🔹 실제값 vs 예측값 산점도
        st.subheader("📈 실제값 vs 예측값")
        full_pred = model.predict(X)
        fig2, ax2 = plt.subplots()
        sns.regplot(x=full_pred, y=y, ax=ax2, ci=95, line_kws={"color": "blue"})
        ax2.set_xlabel("모델이 예측한 값")
        ax2.set_ylabel("실제 비행성능 (F.P)")
        st.pyplot(fig2)

        # 🔹 변수와 비행성능의 관계 시각화
        st.subheader("📉 독립변수 vs 비행성능 (F.P)")
        selected_feature = st.selectbox("변수를 선택하세요", feature_cols)

        # 산점도 + 회귀선
        fig3, ax3 = plt.subplots()
        sns.regplot(data=df, x=selected_feature, y="F.P", ax=ax3,
                    scatter_kws={"alpha": 0.6}, line_kws={"color": "red"})
        ax3.set_xlabel(selected_feature)
        ax3.set_ylabel("비행성능 (F.P)")
        st.pyplot(fig3)

        # 상관계수 계산
        corr = df[selected_feature].corr(df["F.P"])
        st.caption(f"📈 상관계수 (Pearson r): {corr:.2f}")

        # 🔹 예측 입력
        st.subheader("🧪 새 조건 입력 → 비행성능 예측")
        input_data = {}
        for col in feature_cols:
            input_data[col] = st.number_input(col, value=float(X[col].mean()))
        input_df = pd.DataFrame([input_data])
        prediction = model.predict(input_df)[0]
        st.success(f"📈 예측된 비행성능 (F.P): {prediction:.2f}")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")

