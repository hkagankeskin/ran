import streamlit as st
import pandas as pd

# 1. SAYFA YAPILANDIRMASI VE ÖZEL TASARIM (CSS)
st.set_page_config(page_title="RAN Scoring / Puanlama", layout="wide")

# Okul tahtası deseni ve tebeşir beyazı yazı tipi ayarları
st.markdown("""
    <style>
    .stApp {
        background-color: #0d2b1d;
        background-image: url("https://www.transparenttextures.com/patterns/black-chalkboard.png");
        color: #ffffff;
    }
    h1, h2, h3, p, label, .stMetric, span {
        color: #ffffff !important;
        font-family: 'Comic Sans MS', cursive, sans-serif; /* Daha "el yazısı" hissi için */
    }
    .stSidebar {
        background-color: rgba(255, 255, 255, 0.1);
    }
    .stNumberInput input, .stSelectbox div {
        color: #000000 !important; /* Giriş kutularının içi okunabilirlik için siyah kalsın */
    }
    hr {
        border-top: 2px dashed #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DİL SEÇENEKLERİ SÖZLÜĞÜ
texts = {
    "TR": {
        "title": "🎯 RAN Testi Otomatik Puanlama",
        "subtitle": "Hızlı Otomatik İsimlendirme (RAN) Laboratuvarı",
        "sidebar_lang": "Dil / Language",
        "sidebar_header": "Öğrenci Bilgileri",
        "test_type": "Test Türü",
        "age": "Öğrenci Yaşı (Ay)",
        "score": "Test Süresi (Saniye)",
        "test_options": ["Şekil", "Renk", "Sayı"],
        "error_file": "Hata: Dosyalar yüklenemedi!",
        "error_age": "Seçilen yaş için norm tablosunda veri bulunamadı.",
        "eval_header": "Değerlendirme",
        "cat_heavy": "🔴 AĞIR RİSK: Çok Yavaş",
        "cat_risk": "🟡 RİSKLİ: Yavaş",
        "cat_superior": "🟢 ÜSTÜN: Çok Hızlı",
        "cat_normal": "🔵 NORMAL: Beklenen",
        "metric_t": "T-Puanı",
        "metric_p": "Yüzdelik Dilim",
        "metric_r": "Ham Süre",
        "comment": "Yorum: {age} aylık bir çocuk için {test} testinde {score} saniyelik performans, yaşıtlarının %{perc:.1f}'inden daha iyidir."
    },
    "EN": {
        "title": "🎯 RAN Test Automatic Scoring",
        "subtitle": "Rapid Automatized Naming (RAN) Lab",
        "sidebar_lang": "Language / Dil",
        "sidebar_header": "Student Information",
        "test_type": "Test Type",
        "age": "Student Age (Months)",
        "score": "Test Duration (Seconds)",
        "test_options": ["Shape", "Color", "Number"],
        "error_file": "Error: Files could not be loaded!",
        "error_age": "No data found for the selected age in the norm table.",
        "eval_header": "Evaluation",
        "cat_heavy": "🔴 SEVERE RISK: Very Slow",
        "cat_risk": "🟡 AT RISK: Slow",
        "cat_superior": "🟢 SUPERIOR: Very Fast",
        "cat_normal": "🔵 NORMAL: Expected",
        "metric_t": "T-Score",
        "metric_p": "Percentile",
        "metric_r": "Raw Time",
        "comment": "Comment: For a {age}-month-old child, a performance of {score} seconds in the {test} test is better than {perc:.1f}% of their peers."
    }
}

# 3. DİL SEÇİMİ
lang = st.sidebar.radio(texts["TR"]["sidebar_lang"], ["TR", "EN"])
t = texts[lang]

st.title(t["title"])
st.write(t["subtitle"])

# 4. VERİ YÜKLEME
@st.cache_data
def load_data():
    try:
        sekil = pd.read_csv("RAN_Sekil_Tum_Aylar_Norm_Tablosu.csv")
        renk = pd.read_csv("RAN_Renk_Tum_Aylar_Norm_Tablosu.csv")
        sayi = pd.read_csv("RAN_Sayi_Tum_Aylar_Norm_Tablosu.csv")
        return {"Şekil": sekil, "Renk": renk, "Sayı": sayi}
    except Exception as e:
        st.error(f"{t['error_file']} Details: {e}")
        return None

norms = load_data()

if norms:
    # 5. YAN PANEL (Girişler)
    st.sidebar.divider()
    st.sidebar.header(t["sidebar_header"])
    
    test_mapping = {t["test_options"][0]: "Şekil", t["test_options"][1]: "Renk", t["test_options"][2]: "Sayı"}
    secilen_etiket = st.sidebar.selectbox(t["test_type"], t["test_options"])
    test_tipi = test_mapping[secilen_etiket]
    
    yas_ay = st.sidebar.slider(t["age"], 70, 82, 75)
    ham_sure = st.sidebar.number_input(t["score"], 20, 150, 60)

    # 6. HESAPLAMA MANTIĞI (HİÇ DEĞİŞMEDİ)
    df_secili = norms[test_tipi]
    df_yas = df_secili[df_secili['Aylik_Yas'] == yas_ay].copy()

    if not df_yas.empty:
        df_yas['raw_numeric'] = pd.to_numeric(df_yas['raw'], errors='coerce')
        idx = (df_yas['raw_numeric'] - ham_sure).abs().idxmin()
        sonuc_satiri = df_yas.loc[idx]
        
        t_puani = sonuc_satiri['norm']
        yuzdelik = sonuc_satiri['percentile']

        if t_puani <= 30:
            durum = t["cat_heavy"]; renk_kod = "red"
        elif t_puani <= 40:
            durum = t["cat_risk"]; renk_kod = "orange"
        elif t_puani >= 60:
            durum = t["cat_superior"]; renk_kod = "green"
        else:
            durum = t["cat_normal"]; renk_kod = "blue"

        # 7. GÖRSEL SONUÇ EKRANI
        st.divider()
        st.markdown(f"### {t['eval_header']}: :{renk_kod}[{durum}]")
        
        col1, col2, col3 = st.columns(3)
        col1.metric(t["metric_t"], f"{t_puani:.2f}")
        col2.metric(t["metric_p"], f"%{yuzdelik:.1f}")
        col3.metric(t["metric_r"], f"{ham_sure} sn")

        st.info(t["comment"].format(age=yas_ay, test=secilen_etiket, score=ham_sure, perc=yuzdelik))
    else:
        st.warning(t["error_age"])
