import streamlit as st
import pandas as pd

# 1. SAYFA YAPILANDIRMASI VE PROFESYONEL UI (CSS)
st.set_page_config(page_title="RAN Analytics", layout="wide")

# Google Material Symbols Kütüphanesini ve Özel CSS'i ekliyoruz
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* İkon ve Başlık Stili */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    
    .material-symbols-rounded {
        color: #1e3a8a;
        font-size: 28px !important;
    }

    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    .header-logo {
        height: 60px;
        border-radius: 8px;
    }

    h1 {
        color: #1e3a8a !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        margin: 0;
    }
    
    /* Sidebar başlığı için stil */
    .sidebar-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
        color: #334155;
        margin-bottom: 10px;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stMetricValue"] {
        color: #2563eb !important;
        font-size: 1.8rem !important;
    }
    
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BAŞLIK ALANI ---
logo_url = "https://support.renaissance.com/servlet/rtaImage?eid=ka0Nx00000073KX&feoid=00NQg000006K5pm&refid=0EMQg00000IutXM" 

st.markdown(f"""
    <div class="header-container">
        <img src="{logo_url}" class="header-logo" alt="RAN Test İkonu">
        <h1>RAN Analytics System</h1>
    </div>
    """, unsafe_allow_html=True)

st.write("Hızlı Otomatik İsimlendirme (RAN) Klinik Karar Destek Aracı")

# 2. VERİ YÜKLEME
@st.cache_data
def load_data():
    try:
        sekil = pd.read_csv("RAN_Sekil_Tum_Aylar_Norm_Tablosu.csv")
        renk = pd.read_csv("RAN_Renk_Tum_Aylar_Norm_Tablosu.csv")
        sayi = pd.read_csv("RAN_Sayi_Tum_Aylar_Norm_Tablosu.csv")
        return {"Şekil": sekil, "Renk": renk, "Sayı": sayi}
    except Exception as e:
        st.error(f"Sistem Hatası: Veri tabanı yüklenemedi!")
        return None

norms = load_data()

if norms:
    # 3. YAN PANEL (Modern İkonlu Başlık)
    st.sidebar.markdown("""
        <div class="sidebar-title">
            <span class="material-symbols-rounded">tune</span>
            Parametreler
        </div>
        """, unsafe_allow_html=True)
    
    test_tipi = st.sidebar.selectbox("Test Modülü", ["Şekil", "Renk", "Sayı"])
    yas_ay = st.sidebar.slider("Öğrenci Yaşı (Ay)", 70, 82, 75)
    ham_sure = st.sidebar.number_input("Tamamlama Süresi (Saniye)", 20, 150, 60)

    # 4. HESAPLAMA MANTIĞI
    df_secili = norms[test_tipi]
    df_yas = df_secili[df_secili['Aylik_Yas'] == yas_ay].copy()

    if not df_yas.empty:
        df_yas['raw_numeric'] = pd.to_numeric(df_yas['raw'], errors='coerce')
        idx = (df_yas['raw_numeric'] - ham_sure).abs().idxmin()
        sonuc_satiri = df_yas.loc[idx]
        t_puani = sonuc_satiri['norm']
        yuzdelik = sonuc_satiri['percentile']

        # 5. GÖRSEL SONUÇ PANELİ (Modern İkonlu Başlık)
        st.divider()
        st.markdown("""
            <div class="section-header">
                <span class="material-symbols-rounded">query_stats</span>
                <h3 style="margin:0;">Analitik Sonuçlar</h3>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("T-Skoru", f"{t_puani:.2f}")
        col2.metric("Persentil (Yüzdelik)", f"%{yuzdelik:.1f}")
        col3.metric("Ham Veri (sn)", f"{ham_sure}")

        # Dinamik Durum Kartı
        if t_puani <= 30: durum = "🔴 Kritik: Çok Yavaş"
        elif t_puani <= 40: durum = "🟡 Risk: Yavaş"
        elif t_puani >= 60: durum = "🟢 Üstün: Çok Hızlı"
        else: durum = "🔵 Standart: Beklenen Gelişim"

        st.info(f"**{durum}**\n\nAnaliz: {yas_ay} aylık örneklemde {test_tipi} testi için {ham_sure} saniyelik performans, popülasyonun %{yuzdelik:.1f}'inden daha efektif bir hıza işaret eder.")

        # --- 6. KLASİK NORM REFERANS TABLOSU (Modern İkonlu Başlık) ---
        st.divider()
        st.markdown("""
            <div class="section-header">
                <span class="material-symbols-rounded">menu_book</span>
                <h3 style="margin:0;">Klasik Norm Referans Tablosu</h3>
            </div>
            """, unsafe_allow_html=True)
        
        referans_data = {
            "Yaş Grubu": ["66-71 Ay", "72-77 Ay", "78-83 Ay"] * 3,
            "Test": ["Şekil"]*3 + ["Renk"]*3 + ["Sayı"]*3,
            "Çok İyi": ["< 48.9", "< 48.6", "< 48.4", "< 46.8", "< 48.0", "< 44.6", "< 37.0", "< 40.4", "< 36.1"],
            "İyi": ["48.9-62.2", "48.6-62.0", "48.4-60.7", "46.8-72.7", "48.0-69.0", "44.6-67.4", "37.0-57.1", "40.4-57.6", "36.1-53.7"],
            "Normal": ["62.2-75.5", "62.0-75.4", "60.7-73.0", "72.7-98.6", "69.0-90.1", "67.4-90.1", "57.1-77.2", "57.6-74.8", "53.7-71.3"],
            "Zayıf": ["75.5-88.7", "75.4-88.9", "73.0-85.2", "98.6-124.6", "90.1-111.1", "90.1-112.9", "77.2-97.3", "74.8-92.0", "71.3-88.9"],
            "Çok Zayıf": ["> 88.7", "> 88.9", "> 85.2", "> 124.6", "> 111.1", "> 112.9", "> 97.3", "> 92.0", "> 88.9"]
        }
        
        df_ref = pd.DataFrame(referans_data)
        st.dataframe(df_ref, use_container_width=True, hide_index=True)
        st.caption("⚠️ Not: Bu değerler saniye cinsindendir. Düzeyler, örneklem ortalaması ve standart sapma (SD) değerleri baz alınarak hesaplanmıştır.")
        
        # --- 7. AKADEMİK ATIF NOTU ---
        st.write("") 
        st.markdown("<div style='text-align: center; color: gray; font-size: 0.85rem;'>Bu normlama sistemi, Lenhard, Lenhard & Maurice (2018) tarafından R Statistics için geliştirilen cNORM paketi ile yapılmıştır.</div>", unsafe_allow_html=True)

    else:
        st.warning("Seçilen yaş segmenti için norm verisi bulunamadı.")
