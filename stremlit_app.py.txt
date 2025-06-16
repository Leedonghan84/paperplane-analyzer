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

st.title("🛩️ 종이컵 비행기 성능 분석기")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요 (분석용 데이터 포함)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    if "분석용 데이터" in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name="분석용 데이터")
        df = df.iloc[:, :9]

        st.subheader("📋 데이터 미리보기")
        st.dataframe(df.head())

        X = df.drop(columns=["비행성능"])
        y = df["비행성능"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        score = r2_score(y_test, y_pred)
        st.success(f"모델 R² 점수: {score:.2f}")

        st.subheader("🌟 변수 중요도")
        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            "변수": X.columns,
            "중요도": importances
        }).sort_values(by="중요도", ascending=False)

        fig1, ax1 = plt.subplots()
        sns.barplot(data=importance_df, x="중요도", y="변수", ax=ax1)
        st.pyplot(fig1)

        st.subheader("📈 실제값 vs 예측값")
        fig2, ax2 = plt.subplots()
        sns.scatterplot(x=y_test, y=y_pred, ax=ax2)
        ax2.set_xlabel("실제값")
        ax2.set_ylabel("예측값")
        ax2.set_title("모델 성능 비교")
        st.pyplot(fig2)

        st.subheader("🧪 새 조건으로 비행성능 예측하기")
        input_data = {}
        for col in X.columns:
            val = st.number_input(col, value=float(X[col].mean()))
            input_data[col] = val

        input_df = pd.DataFrame([input_data])
        prediction = model.predict(input_df)[0]
        st.success(f"예측된 비행성능: {prediction:.4f}")

    else:
        st.error("엑셀에 '분석용 데이터' 시트가 없습니다.")
