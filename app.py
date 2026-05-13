import streamlit as st
import pandas as pd

# 1. SAYFA YAPILANDIRMASI VE PROFESYONEL UI (CSS)
st.set_page_config(page_title="RAN Analytics", layout="wide")

# Modern, kurumsal ve ferah bir tasarım için CSS
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Başlıklar ve Fontlar */
    h1 {
        color: #1e3a8a !important; /* Kurumsal Lacivert */
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h3 {
        color: #334155 !important;
        font-weight: 600;
    }

    /* Sidebar Tasarımı */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Metrik Kartları Özelleştirme */
    [data-testid="stMetricValue"] {
        color: #2563eb !important; /* Profesyonel Mavi */
        font-size: 1.8rem !important;
    }
    
    /* Bilgi Kutuları (st.info) */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Divider Çizgisi */
    hr {
        border-top: 1px solid #cbd5e1 !important;
    }
    
    /* Giriş Elemanları */
    .stNumberInput div, .stSelectbox div {
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DİL SEÇENEKLERİ SÖZLÜĞÜ (Değişmedi)
texts = {
    "TR": {
        "title": "RAN Analytics System",
        "subtitle": "Hızlı Otomatik İsimlendirme (RAN) Klinik Karar Destek Aracı",
        "sidebar_lang": "Uygulama Dili / App Language",
        "sidebar_header": "Parametreler",
        "test_type": "Test Modülü",
        "age": "Öğrenci Yaşı (Ay)",
        "score": "Tamamlama Süresi (Saniye)",
        "test_options": ["Şekil", "Renk", "Sayı"],
        "error_file": "Sistem Hatası: Veri tabanı yüklenemedi!",
        "error_age": "Seçilen yaş segmenti için norm verisi bulunamadı.",
        "eval_header": "Analitik Sonuçlar",
        "cat_heavy": "🔴 Kritik: Çok Yavaş",
        "cat_risk": "🟡 Risk: Yavaş",
        "cat_superior": "🟢 Üstün: Çok Hızlı",
        "cat_normal": "🔵 Standart: Beklenen Gelişim",
        "metric_t": "T-Skoru",
        "metric_p": "Persentil (Yüzdelik)",
        "metric_r": "Ham Veri (sn)",
        "comment": "Analiz: {age} aylık örneklemde {test} testi için {score} saniyelik performans, popülasyonun %{perc:.1f}'inden daha efektif bir hıza işaret eder."
    },
    "EN": {
        "title": "RAN Analytics System",
        "subtitle": "Rapid Automatized Naming (RAN) Clinical Decision Support Tool",
        "sidebar_lang": "App Language / Uygulama Dili",
        "sidebar_header": "Parameters",
        "test_type": "Test Module",
        "age": "Student Age (Months)",
        "score": "Completion Time (Seconds)",
        "test_options": ["Shape", "Color", "Number"],
        "error_file": "System Error: Database could not be loaded!",
        "error_age": "No norm data found for the selected age segment.",
        "eval_header": "Analytical Results",
        "cat_heavy": "🔴 Critical: Very Slow",
        "cat_risk": "🟡 At Risk: Slow",
        "cat_superior": "🟢 Superior: Very Fast",
        "cat_normal": "🔵 Standard: Expected Development",
        "metric_t": "T-Score",
        "metric_p": "Percentile",
        "metric_r": "Raw Time (sec)",
        "comment": "Analysis: For a {age}-month-old sample, a performance of {score}s in the {test} test indicates a velocity more effective than {perc:.1f}% of the population."
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
        st.error(f"{t['error_file']} Log: {e}")
        return None

norms = load_data()

if norms:
    # 5. YAN PANEL
    st.sidebar.divider()
    st.sidebar.subheader(t["sidebar_header"])
    
    test_mapping = {t["test_options"][0]: "Şekil", t["test_options"][1]: "Renk", t["test_options"][2]: "Sayı"}
    secilen_etiket = st.sidebar.selectbox(t["test_type"], t["test_options"])
    test_tipi = test_mapping[secilen_etiket]
    
    yas_ay = st.sidebar.slider(t["age"], 70, 82, 75)
    ham_sure = st.sidebar.number_input(t["score"], 20, 150, 60)

    # 6. HESAPLAMA MANTIĞI (Korumalı)
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

        # 7. GÖRSEL SONUÇ PANELİ
        st.divider()
        st.subheader(t['eval_header'])
        
        # Sonuç Metrikleri
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(t["metric_t"], f"{t_puani:.2f}")
        with m_col2:
            st.metric(t["metric_p"], f"%{yuzdelik:.1f}")
        with m_col3:
            st.metric(t["metric_r"], f"{ham_sure}")

        # Durum Kartı
        st.info(f"**{durum}**\n\n{t['comment'].format(age=yas_ay, test=secilen_etiket, score=ham_sure, perc=yuzdelik)}")
    else:
        st.warning(t["error_age"])
