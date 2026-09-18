import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

from utils.fusion import fusion_prediction


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AgriSmart AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ------------------------------------------------------------
# Helper: st.markdown() treats a line starting with 4+ leading
# spaces as a Markdown "indented code block", and a blank line
# ends an in-progress raw-HTML block early. Our HTML snippets are
# written inside nested `if`/`with` blocks (so different tags sit
# at different indentation levels) and contain blank lines between
# paragraphs for readability — either one is enough to make
# Streamlit render the tags as literal text instead of HTML.
# Stripping every line individually and dropping blank lines
# removes both triggers at once.
# ------------------------------------------------------------

def render_html(html: str) -> None:
    lines = [line.strip() for line in html.strip().splitlines()]
    cleaned = "\n".join(line for line in lines if line != "")
    st.markdown(cleaned, unsafe_allow_html=True)


# ============================================================
# CUSTOM CSS
# ============================================================

render_html(
    """
    <style>

    /* Hide Streamlit's default chrome — no sidebar toggle, no menu, no footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent;
        height: 0px;
    }
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}

    .stApp {
        background-color: #f5f8f6;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }

    /* ---------------------------------------------------------
       FORCE READABLE COLORS for Streamlit's own widgets.
       These win regardless of whether the visitor's OS/browser
       is set to dark mode (config.toml already pins the app to
       the light theme — this is a second safety net).
       --------------------------------------------------------- */

    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h5,
    [data-testid="stMarkdownContainer"] h6 {
        color: #123d2a !important;
    }

    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: #2c4136 !important;
        font-weight: 600 !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background-color: #ffffff !important;
        border: 1.5px dashed #b6cfc0 !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #2c4136 !important;
    }
    [data-testid="stFileUploader"] section button {
        background-color: #ffffff !important;
        color: #123d2a !important;
        border: 1px solid #cfe0d6 !important;
    }

    [data-testid="stNumberInput"] input {
        background-color: #ffffff !important;
        color: #17301f !important;
        border: 1px solid #cfe0d6 !important;
    }
    [data-testid="stNumberInputStepUp"],
    [data-testid="stNumberInputStepDown"] {
        background-color: #ffffff !important;
        color: #17301f !important;
    }

    [data-testid="stAlert"] p {
        color: #17301f !important;
    }

    [data-testid="stMetric"] label,
    [data-testid="stMetricValue"] {
        color: #123d2a !important;
    }

    [data-testid="stCaptionContainer"] p {
        color: #6b7d74 !important;
    }

    [data-testid="stExpander"] summary {
        color: #123d2a !important;
    }
    [data-testid="stExpander"] summary span {
        color: #123d2a !important;
    }
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] strong {
        color: #2c4136 !important;
    }

    button[kind="primary"] p {
        color: #ffffff !important;
    }

    /* ---------------------------------------------------------
       Layout components
       --------------------------------------------------------- */

    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #ffffff;
        border: 1px solid #e1e9e4;
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .app-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .app-logo { font-size: 30px; line-height: 1; }

    .app-title {
        font-size: 24px;
        font-weight: 800;
        color: #123d2a !important;
        margin: 0;
        line-height: 1.1;
    }

    .app-subtitle {
        font-size: 13px;
        color: #6b7d74 !important;
        margin: 2px 0 0 0;
    }

    .status-pill {
        display: flex;
        align-items: center;
        gap: 6px;
        background: #e5f6ed;
        color: #16804c !important;
        font-size: 13px;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #16804c;
        display: inline-block;
    }

    .section-title {
        font-size: 19px;
        font-weight: 700;
        color: #163d2c !important;
        margin-top: 4px;
        margin-bottom: 10px;
    }

    .metric-card {
        background: white;
        border: 1px solid #e1e9e4;
        border-radius: 14px;
        padding: 14px 16px;
        min-height: 100px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .metric-label { font-size: 12.5px; color: #687a71 !important; margin-bottom: 4px; }
    .metric-value { font-size: 20px; font-weight: 700; color: #173f2c !important; }
    .metric-icon { font-size: 18px; margin-bottom: 4px; }

    .result-card {
        background: white;
        border-radius: 16px;
        padding: 18px;
        border: 1px solid #e1e9e4;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        min-height: 150px;
    }
    .result-title { font-size: 13px; color: #6b7d74 !important; margin-bottom: 6px; letter-spacing: 0.3px; }
    .result-value { font-size: 22px; font-weight: 700; color: #123d2a !important; line-height: 1.2; }
    .result-small { font-size: 13px; color: #63756c !important; margin-top: 6px; }

    .risk-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #e1e9e4;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        min-height: 150px;
    }
    .risk-value { font-size: 26px; font-weight: 800; }
    .risk-high { color: #c73535 !important; }
    .risk-moderate { color: #a96800 !important; }
    .risk-low { color: #16804c !important; }

    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12.5px;
        font-weight: 600;
        margin-top: 8px;
    }
    .badge-green { background: #e5f6ed; color: #16804c !important; }
    .badge-orange { background: #fff2dd; color: #a96800 !important; }
    .badge-red { background: #fde8e8; color: #c73535 !important; }

    .report-box {
        background: white;
        border: 1px solid #e1e9e4;
        border-radius: 16px;
        padding: 20px 22px;
        line-height: 1.55;
        color: #34483e !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        font-size: 14.5px;
    }
    .report-box p { margin: 4px 0 12px 0; color: #34483e !important; }
    .report-heading { font-size: 15.5px; font-weight: 700; color: #16432e !important; margin-bottom: 4px; }

    .recommendation-box {
        background: #eef9f3;
        border: 1px solid #cfe9da;
        border-radius: 16px;
        padding: 18px 20px;
        color: #254d39 !important;
        line-height: 1.5;
        font-size: 14.5px;
    }
    .recommendation-box p { margin: 4px 0; color: #254d39 !important; }

    .note { color: #718078 !important; font-size: 12.5px; }

    div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }

    </style>
    """
)


# ============================================================
# HEADER
# ============================================================

render_html(
    """
    <div class="app-header">
        <div class="app-header-left">
            <div class="app-logo">🌱</div>
            <div>
                <p class="app-title">AgriSmart AI</p>
                <p class="app-subtitle">Multimodal Plant Health &amp; Irrigation Assessment</p>
            </div>
        </div>
        <div class="status-pill">
            <span class="status-dot"></span> System Online
        </div>
    </div>
    """
)


# ============================================================
# INPUT SECTION
# ============================================================

render_html('<div class="section-title">🔍 Plant Analysis</div>')

input_col1, input_col2 = st.columns([1.05, 1])


# ---------------- IMAGE INPUT ----------------

with input_col1:

    st.markdown("##### 🌿 Plant Leaf Image")

    uploaded_file = st.file_uploader(
        "Upload a leaf image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="leaf_image_uploader"
    )

    image = None

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Plant Leaf", use_container_width=True)
    else:
        st.info("Upload a clear plant leaf image for CNN disease analysis.")


# ---------------- SENSOR INPUT ----------------

with input_col2:

    st.markdown("##### 🌡 Environmental & Soil Data")

    sensor_col1, sensor_col2 = st.columns(2)

    with sensor_col1:
        soil_moisture = st.number_input("Soil Moisture (%)", min_value=0.0, max_value=100.0, value=35.0, step=0.1, key="soil_moisture_input")
        soil_temperature = st.number_input("Soil Temperature (°C)", value=25.0, step=0.1, key="soil_temperature_input")
        soil_ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=6.5, step=0.1, key="soil_ph_input")

    with sensor_col2:
        humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=60.0, step=0.1, key="humidity_input")
        air_temperature = st.number_input("Air Temperature (°C)", value=30.0, step=0.1, key="air_temperature_input")
        solar_radiation = st.number_input("Solar Radiation (W/m²)", min_value=0.0, value=700.0, step=10.0, key="solar_radiation_input")


st.write("")

analyze = st.button("🌿 Analyze Plant", type="primary", use_container_width=True, key="analyze_button")


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    if uploaded_file is None:
        st.warning("Please upload a plant leaf image before starting the analysis.")

    else:

        with st.spinner("Running CNN and sensor models..."):

            result = fusion_prediction(
                image=image,
                soil_moisture=soil_moisture,
                soil_temperature=soil_temperature,
                soil_ph=soil_ph,
                humidity=humidity,
                air_temperature=air_temperature,
                solar_radiation=solar_radiation
            )

        image_result = result["image_analysis"]
        sensor_result = result["sensor_analysis"]

        disease_name = image_result["plant_disease"]
        disease_confidence = image_result["disease_confidence"]
        top_3 = image_result["top_3_predictions"]

        irrigation_needed = sensor_result["irrigation_needed"]
        irrigation_probability = sensor_result["irrigation_probability"]
        recommended_liters = sensor_result["recommended_irrigation_liters"]

        readings = sensor_result["sensor_readings"]

        is_healthy = "healthy" in disease_name.lower()

        if is_healthy:
            risk_level, risk_class, risk_badge = "Low", "risk-low", "badge-green"
        elif disease_confidence >= 0.70:
            risk_level, risk_class, risk_badge = "High", "risk-high", "badge-red"
        else:
            risk_level, risk_class, risk_badge = "Moderate", "risk-moderate", "badge-orange"

        readable_disease = disease_name.replace("_", " ")

        # ---------------- REPORT HEADER ----------------

        st.divider()
        render_html('<div class="section-title">📋 Plant Health Assessment Report</div>')

        # ---------------- TOP SUMMARY CARDS ----------------

        card1, card2, card3, card4 = st.columns(4)

        with card1:
            render_html(f"""
            <div class="result-card">
                <div class="result-title">🌿 VISUAL ANALYSIS</div>
                <div class="result-value">{readable_disease}</div>
                <div class="result-small">CNN prediction</div>
            </div>
            """)

        with card2:
            render_html(f"""
            <div class="result-card">
                <div class="result-title">📊 CNN CONFIDENCE</div>
                <div class="result-value">{disease_confidence * 100:.2f}%</div>
                <div class="result-small">Confidence of top prediction</div>
            </div>
            """)

        with card3:
            irrigation_status = "Irrigation Needed" if irrigation_needed == 1 else "Irrigation Not Needed"
            irrigation_badge = "badge-orange" if irrigation_needed == 1 else "badge-green"
            render_html(f"""
            <div class="result-card">
                <div class="result-title">💧 IRRIGATION ASSESSMENT</div>
                <div class="result-value">{recommended_liters:.2f} L</div>
                <div class="result-small">Recommended irrigation amount</div>
                <span class="badge {irrigation_badge}">{irrigation_status}</span>
            </div>
            """)

        with card4:
            render_html(f"""
            <div class="risk-card">
                <div class="result-title">🩺 OVERALL RISK</div>
                <div class="risk-value {risk_class}">{risk_level}</div>
                <div class="result-small">Based on visual + sensor fusion</div>
                <span class="badge {risk_badge}">{disease_confidence * 100:.0f}% confidence</span>
            </div>
            """)

        # ---------------- LIVE SENSOR READINGS ----------------

        st.write("")

        s1, s2, s3, s4, s5 = st.columns(5)

        sensor_cards = [
            (s1, "💧", "Soil Moisture", f"{readings['soil_moisture_pct']:.1f}%"),
            (s2, "🌡️", "Soil Temp", f"{readings['soil_temperature_c']:.1f} °C"),
            (s3, "🧪", "Soil pH", f"{readings['soil_ph']:.1f}"),
            (s4, "☁️", "Humidity", f"{readings['humidity_pct']:.1f}%"),
            (s5, "☀️", "Solar Rad.", f"{readings['solar_radiation_w_m2']:.0f} W/m²"),
        ]

        for column, icon, label, value in sensor_cards:
            with column:
                render_html(f"""
                <div class="metric-card">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """)

        # ---------------- IMAGE + IRRIGATION GAUGE ----------------

        st.write("")

        left, right = st.columns(2)

        with left:
            render_html('<div class="section-title">🌿 Visual Analysis</div>')
            st.image(image, use_container_width=True)
            if is_healthy:
                st.success("Top prediction is a healthy class.")
            else:
                st.warning("Top prediction belongs to a disease class.")

        with right:
            render_html('<div class="section-title">💧 Irrigation Model</div>')

            gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=irrigation_probability * 100,
                    number={"suffix": "%"},
                    title={"text": "Irrigation Probability"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"thickness": 0.25, "color": "#16804c"},
                        "steps": [
                            {"range": [0, 50], "color": "#e5f6ed"},
                            {"range": [50, 75], "color": "#fff2dd"},
                            {"range": [75, 100], "color": "#fde8e8"},
                        ],
                    },
                )
            )
            gauge.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
            st.plotly_chart(gauge, use_container_width=True)

            irr_col1, irr_col2 = st.columns(2)
            with irr_col1:
                st.metric("Model Decision", "Needed" if irrigation_needed == 1 else "Not Needed")
            with irr_col2:
                st.metric("Recommended Water", f"{recommended_liters:.2f} L")

        # ---------------- CNN TOP-3 CHART (own full-width row so
        # the bars have room and don't look squeezed) ----------------

        st.write("")
        render_html('<div class="section-title">📊 CNN Prediction Breakdown</div>')

        cnn_chart_data = {
            "Condition": [item["class"].replace("_", " ") for item in top_3],
            "Probability": [item["probability"] * 100 for item in top_3],
        }

        fig_cnn = px.bar(
            cnn_chart_data,
            x="Probability",
            y="Condition",
            orientation="h",
            text="Probability"
        )
        fig_cnn.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            marker_color="#16804c"
        )
        fig_cnn.update_layout(
            xaxis_title="Prediction Probability (%)",
            yaxis_title="",
            xaxis=dict(range=[0, 100]),
            yaxis=dict(autorange="reversed"),
            height=320,
            margin=dict(l=10, r=60, t=20, b=40),
            font=dict(size=14),
        )
        st.plotly_chart(fig_cnn, use_container_width=True)
        st.caption("The chart shows the three highest-probability classes returned by the CNN.")

        # ---------------- OVERALL REPORT ----------------

        st.divider()
        render_html('<div class="section-title">📝 Analysis Summary</div>')

        irrigation_text = (
            "The irrigation classifier indicates that irrigation is needed."
            if irrigation_needed == 1
            else "The irrigation classifier indicates that irrigation is not currently needed."
        )

        render_html(f"""
        <div class="report-box">
            <div class="report-heading">🌿 Visual Analysis</div>
            <p>
                The CNN classified the uploaded leaf image as
                <b>{readable_disease}</b>, with a confidence of
                <b>{disease_confidence * 100:.2f}%</b>.
            </p>

            <div class="report-heading">💧 Irrigation Analysis</div>
            <p>
                {irrigation_text}
                The model's irrigation probability is
                <b>{irrigation_probability * 100:.2f}%</b>, and the regression model
                estimates approximately <b>{recommended_liters:.2f} litres</b> of irrigation.
            </p>

            <div class="report-heading">🌡 Environmental Context</div>
            <p>
                Current readings: <b>{readings['soil_moisture_pct']:.1f}%</b> soil moisture,
                <b>{readings['soil_temperature_c']:.1f} °C</b> soil temperature,
                pH <b>{readings['soil_ph']:.1f}</b>,
                <b>{readings['humidity_pct']:.1f}%</b> humidity,
                <b>{readings['air_temperature_c']:.1f} °C</b> air temperature, and
                <b>{readings['solar_radiation_w_m2']:.1f} W/m²</b> solar radiation.
            </p>

            <div class="report-heading">🔎 Combined Interpretation</div>
            <p style="margin-bottom:0;">
                AgriSmart AI combines visual evidence from the CNN with environmental and soil
                context from the sensor models. The sensor model supports irrigation assessment
                and environmental context; it should not be treated as proof of the cause of a
                visually detected disease.
            </p>
        </div>
        """)

        # ---------------- RECOMMENDATIONS ----------------

        st.write("")
        render_html('<div class="section-title">💡 Recommended Next Steps</div>')

        recommendations = []

        if is_healthy:
            recommendations.append("Continue monitoring the plant for visible changes.")
        else:
            recommendations.append("Inspect the affected leaves and nearby leaves for similar visible symptoms.")
            recommendations.append("Monitor whether the visible symptoms spread or change over time.")

        if irrigation_needed == 1:
            recommendations.append(
                f"Consider providing approximately {recommended_liters:.2f} L of water according to the irrigation model."
            )
        else:
            recommendations.append("Avoid unnecessary irrigation based on the current irrigation-model result.")

        recommendations.append("Continue monitoring soil and environmental conditions.")

        bullets = "".join(f"<p>• {item}</p>" for item in recommendations)
        render_html(f'<div class="recommendation-box">{bullets}</div>')

        # ---------------- MODEL INFO + DISCLAIMER ----------------

        with st.expander("ℹ️ Model Information"):
            st.write("**CNN:** MobileNetV2-based image classification model trained for 15 plant-condition classes.")
            st.write("**Irrigation Classifier:** Random Forest classifier for irrigation-needed prediction.")
            st.write("**Irrigation Regressor:** Random Forest regression model for recommended irrigation volume.")
            st.write("**Fusion:** The application combines the outputs of the image and sensor models at the decision/output level.")

        render_html("""
        <div class="note">
        ⚠️ <b>Important:</b> AgriSmart AI provides AI-based supporting information from image and
        sensor analysis. Results should not be treated as a definitive agricultural diagnosis.
        </div>
        """)