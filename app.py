import streamlit as st
import pandas as pd

# 1. SAYFA YAPILANDIRMASI VE PROFESYONEL UI (CSS)
st.set_page_config(page_title="RAN Analytics", layout="wide")

# Stabil ve hatasız CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }
    .header-logo { height: 60px; border-radius: 8px; }
    h1 { color: #1e3a8a !important; font-family: 'Inter', sans-serif; font-weight: 700; margin: 0; }
    [data-testid="stMetricValue"] { color: #2563eb !important; font-size: 1.8rem !important; }
    .stAlert { border-radius: 12px; border: none; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    hr { border-top: 1px solid #cbd5e1 !important; }
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
    # 3. YAN PANEL (PARAMETRELER)
    st.sidebar.subheader("⚙️ Parametreler")
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

        # Kategori Belirleme
        if t_puani <= 30: durum = "🔴 Kritik: Çok Yavaş"
        elif t_puani <= 40: durum = "🟡 Risk: Yavaş"
        elif t_puani >= 60: durum = "🟢 Üstün: Çok Hızlı"
        else: durum = "🔵 Standart: Beklenen Gelişim"

        # 5. GÖRSEL SONUÇ PANELİ
        st.divider()
        st.subheader("📈 Analitik Sonuçlar")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("T-Skoru", f"{t_puani:.2f}")
        col2.metric("Persentil (Yüzdelik)", f"%{yuzdelik:.1f}")
        col3.metric("Ham Veri (sn)", f"{ham_sure}")

        st.info(f"**{durum}**\n\nAnaliz: {yas_ay} aylık örneklemde {test_tipi} testi için {ham_sure} saniyelik performans, popülasyonun %{yuzdelik:.1f}'inden daha efektif bir hıza işaret eder.")

        # 6. KLASİK NORM REFERANS TABLOSU
        st.divider()
        st.subheader("📚 Klasik Norm Referans Tablosu (Tüm Testler)")
        
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

        # --- 7. KURUMSAL LOGOLAR (BURAYA EKLENDİ) ---
        st.write("") # Küçük bir boşluk
        l_col1, l_col2, l_col3, l_col4 = st.columns(4)

        with l_col1:
            st.image("https://upload.wikimedia.org/wikipedia/tr/b/b8/Hacettepe_Universitesi_Logo.png", width=80)
        with l_col2:
            st.image("https://upload.wikimedia.org/wikipedia/tr/0/08/Duzce_Universitesi_logo.png", width=80)
        with l_col3:
            st.image("https://web.uri.edu/wp-content/themes/uri-main/images/uri-logo.png", width=110)
        with l_col4:
            st.image("https://www.r-project.org/logo/Rlogo.png", width=80)

        # --- 8. AKADEMİK ATIF NOTU ---
        st.write("") 
        st.markdown("<div style='text-align: center; color: gray; font-size: 0.85rem;'>Bu normlama sistemi, Lenhard, Lenhard & Maurice (2018) tarafından R Statistics için geliştirilen cNORM paketi ile yapılmıştır.</div>", unsafe_allow_html=True)

    else:
        st.warning("Seçilen yaş segmenti için norm verisi bulunamadı.")
