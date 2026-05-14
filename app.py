import streamlit as st
import pandas as pd

# 1. SAYFA YAPILANDIRMASI VE PROFESYONEL UI (CSS) (GÜNCELLENDİ)
st.set_page_config(page_title="RAN Analytics", layout="wide")

# Modern, kurumsal ve ferah bir tasarım için CSS (Logo için güncellendi)
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Başlık Alanı (Logo ve Yazı Yan Yana) */
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px; /* Logo ve yazı arasındaki boşluk */
        margin-bottom: 20px;
    }

    .header-logo {
        height: 60px; /* Logo yüksekliği */
        border-radius: 8px; /* İsteğe bağlı yuvarlatılmış köşe */
    }

    h1 {
        color: #1e3a8a !important; /* Kurumsal Lacivert */
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0; /* Boşluğu kaldır */
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

# 2. DİL SEÇENEKLERİ SÖZLÜĞÜ (Tablo Başlıkları Eklendi)
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
        "comment": "Analiz: {age} aylık örneklemde {test} testi için {score} saniyelik performans, popülasyonun %{perc:.1f}'inden daha efektif bir hıza işaret eder.",
        "ref_table_title": "Klasik Norm Referans Tablosu",
        "ref_note": "Not: Bu değerler gerçek veri setinizdeki Ortalama ve Standart Sapma (SD) değerlerine göre oluşturulmuştur.",
        "levels": ["Yaş Grubu", "Çok İyi", "İyi", "Normal", "Zayıf", "Çok Zayıf"]
    },
    "EN": {
        "title": "RAN Analytics System",
        "subtitle": "Rapid Automatized Naming (RAN) Clinical Decision Support Tool",
        "sidebar_lang": "App Language / Uygulama Dili",
        "sidebar_header": "Parameters",
        "test_type": "Test Module",
        "age": "Student Age (Months)",
        "score": "Test Duration (Seconds)",
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
        "comment": "Analysis: For a {age}-month-old sample, a performance of {score}s in the {test} test indicates a velocity more effective than {perc:.1f}% of the population.",
        "ref_table_title": "Classical Norm Reference Table",
        "ref_note": "Note: These values are generated based on the Mean and Standard Deviation (SD) of your actual dataset.",
        "levels": ["Age Group", "Very Good", "Good", "Normal", "Weak", "Very Weak"]
    }
}

# 3. DİL SEÇİMİ
lang = st.sidebar.radio(texts["TR"]["sidebar_lang"], ["TR", "EN"])
t = texts[lang]

# --- BAŞLIK ALANI ---
logo_url = "https://support.renaissance.com/servlet/rtaImage?eid=ka0Nx00000073KX&feoid=00NQg000006K5pm&refid=0EMQg00000IutXM" 

st.markdown(f"""
    <div class="header-container">
        <img src="{logo_url}" class="header-logo" alt="RAN Test Icon">
        <h1>{t["title"]}</h1>
    </div>
    """, unsafe_allow_html=True)

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

    # 6. HESAPLAMA MANTIĞI
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
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(t["metric_t"], f"{t_puani:.2f}")
        with m_col2:
            st.metric(t["metric_p"], f"%{yuzdelik:.1f}")
        with m_col3:
            st.metric(t["metric_r"], f"{ham_sure}")

        st.info(f"**{durum}**\n\n{t['comment'].format(age=yas_ay, test=secilen_etiket, score=ham_sure, perc=yuzdelik)}")

        # --- 8. KLASİK NORM REFERANS TABLOLARI (YENİ EKLENEN KISIM) ---
        st.divider()
        st.subheader(f"📊 {t['ref_table_title']}")

        referans_verileri = {
            "Şekil": {
                t["levels"][0]: ["66-71 Ay", "72-77 Ay", "78-83 Ay"],
                t["levels"][1]: ["< 48.9", "< 48.6", "< 48.4"],
                t["levels"][2]: ["48.9 - 62.2", "48.6 - 62.0", "48.4 - 60.7"],
                t["levels"][3]: ["62.2 - 75.5", "62.0 - 75.4", "60.7 - 73.0"],
                t["levels"][4]: ["75.5 - 88.7", "75.4 - 88.9", "73.0 - 85.2"],
                t["levels"][5]: ["> 88.7", "> 88.9", "> 85.2"]
            },
            "Renk": {
                t["levels"][0]: ["66-71 Ay", "72-77 Ay", "78-83 Ay"],
                t["levels"][1]: ["< 46.8", "< 48.0", "< 44.6"],
                t["levels"][2]: ["46.8 - 72.7", "48.0 - 69.0", "44.6 - 67.4"],
                t["levels"][3]: ["72.7 - 98.6", "69.0 - 90.1", "67.4 - 90.1"],
                t["levels"][4]: ["98.6 - 124.6", "90.1 - 111.1", "90.1 - 112.9"],
                t["levels"][5]: ["> 124.6", "> 111.1", "> 112.9"]
            },
            "Sayı": {
                t["levels"][0]: ["66-71 Ay", "72-77 Ay", "78-83 Ay"],
                t["levels"][1]: ["< 37.0", "< 40.4", "< 36.1"],
                t["levels"][2]: ["37.0 - 57.1", "40.4 - 57.6", "36.1 - 53.7"],
                t["levels"][3]: ["57.1 - 77.2", "57.6 - 74.8", "53.7 - 71.3"],
                t["levels"][4]: ["77.2 - 97.3", "74.8 - 92.0", "71.3 - 88.9"],
                t["levels"][5]: ["> 97.3", "> 92.0", "> 88.9"]
            }
        }

        # Seçilen teste göre ilgili tabloyu DataFrame olarak oluştur ve bas
        current_ref_df = pd.DataFrame(referans_verileri[test_tipi])
        st.table(current_ref_df)
        st.caption(t["ref_note"])

    else:
        st.warning(t["error_age"])
