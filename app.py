import streamlit as st
import pandas as pd
import os

# --- 1. SAYFA YAPILANDIRMASI (HER ZAMAN EN ÜSTTE) ---
st.set_page_config(page_title="RAN Analytics", layout="wide")

# --- 2. SECRETS TEMELLİ ŞİFRE KONTROLÜ ---
def check_password():
    """Secrets üzerinden şifre kontrolü yapar."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Giriş Ekranı Tasarımı
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🔐 RAN Karar Destek Aracı</h2>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        entered_password = st.text_input("Lütfen erişim şifresini giriniz", type="password")
        if st.button("Giriş Yap"):
            if entered_password == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Hatalı şifre. Lütfen yetkili ile iletişime geçiniz.")
    return False

# --- 3. UYGULAMA ANA DÖNGÜSÜ ---
if check_password():
    # Gelişmiş Kurumsal CSS Kuralları
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

    # --- BAŞLIK VE LOGO ALANI ---
    logo_url = "https://support.renaissance.com/servlet/rtaImage?eid=ka0Nx00000073KX&feoid=00NQg000006K5pm&refid=0EMQg00000IutXM" 
    st.markdown(f"""
        <div class="header-container">
            <img src="{logo_url}" class="header-logo" alt="RAN Logo">
            <h1>RAN Analytics System</h1>
        </div>
        """, unsafe_allow_html=True)

    st.write("Hızlı Otomatik İsimlendirme (RAN) Klinik Karar Destek Aracı")

    # --- 4. OPTİMİZE VERİ YÜKLEME KATMANI (4 GÜNCEL MODÜL) ---
    @st.cache_data
    def load_data():
        try:
            # R'da ürettiğimiz 70-96 ve 83-96 arası matrisler çekiliyor
            sekil = pd.read_csv("RAN_Sekil_Tum_Aylar_Norm_Tablosu.csv")
            renk = pd.read_csv("RAN_Renk_Tum_Aylar_Norm_Tablosu.csv")
            sayi = pd.read_csv("RAN_Sayi_Tum_Aylar_Norm_Tablosu.csv")
            harf = pd.read_csv("RAN_Harf_Tum_Aylar_Norm_Tablosu.csv")
            return {"Şekil": sekil, "Renk": renk, "Sayı": sayi, "Harf": harf}
        except Exception:
            st.error("Sistem Hatası: Gelişmiş norm veritabanı yüklenemedi!")
            return None

    norms = load_data()

    if norms:
        # --- 5. YAN PANEL (YENİ DİNAMİK YAŞ VE SÜRE MİMARİSİ) ---
        st.sidebar.subheader("⚙️ Parametreler")
        test_tipi = st.sidebar.selectbox("Test Modülü", ["Şekil", "Renk", "Sayı", "Harf"])
        
        # Yaş sınırları modüllerin yeni bilimsel kapsama alanlarına göre kısıtlanıyor:
        if test_tipi == "Harf":
            # Harf testi sadece okuma bilen 2. sınıfları kapsıyor (83 - 96 ay)
            yas_ay = st.sidebar.slider("Öğrenci Yaşı (Ay)", 83, 96, 88)
        else:
            # Şekil, Renk ve Sayı artık 1 ve 2. sınıfların tamamını kapsıyor (70 - 96 ay)
            yas_ay = st.sidebar.slider("Öğrenci Yaşı (Ay)", 70, 96, 75)
            
        # Yarımşar saniyelik çözünürlük için adımı (step) 0.5 yapıyoruz
        ham_sure = st.sidebar.number_input("Tamamlama Süresi (Saniye)", 10.0, 150.0, 60.0, step=0.5)

        # --- 6. HESAPLAMA VE EN YAKIN MATRİS HÜCRESİNİ BULMA ---
        df_secili = norms[test_tipi]
        
        # Seçilen yaş ayındaki norm satırları filtreleniyor
        df_yas = df_secili[df_secili['Aylik_Yas'] == yas_ay].copy()

        if not df_yas.empty:
            df_yas['raw_numeric'] = pd.to_numeric(df_yas['raw'], errors='coerce')
            
            # Girilen süreye en yakın ham puan satırı matematiksel olarak yakalanıyor
            idx = (df_yas['raw_numeric'] - ham_sure).abs().idxmin()
            sonuc_satiri = df_yas.loc[idx]
            
            t_puani = sonuc_satiri['norm']
            yuzdelik = sonuc_satiri['percentile']

            # Klinik Tanı Ölçütleri Sınıflandırması
            if t_puani <= 30: durum = "🔴 Kritik: Çok Yavaş Performans"
            elif t_puani <= 40: durum = "🟡 Risk: Yavaş Otomatizasyon"
            elif t_puani >= 60: durum = "🟢 Üstün: Çok Hızlı Otomatizasyon"
            else: durum = "🔵 Standart: Beklenen Gelişim Seviyesi"

            # --- 7. KLİNİK RAPORLAMA VE METRİKLER ---
            st.divider()
            st.subheader("📈 Analitik Sonuçlar")
            col1, col2, col3 = st.columns(3)
            col1.metric("T-Skoru", f"{t_puani:.2f}")
            col2.metric("Persentil (Yüzdelik)", f"%{yuzdelik:.1f}")
            col3.metric("Ham Süre", f"{ham_sure} sn")
            
            st.info(f"**{durum}**\n\nAnaliz: {yas_ay} aylık norm grubunda {test_tipi} testi için girilen {ham_sure} saniyelik performans, akran popülasyonunun %{yuzdelik:.1f}'inden daha efektif bir otomatizasyon hızına işaret eder.")

            # --- 8. REFERANS TABLOSU GÖSTERİMİ (Harf Hariç Esneklik) ---
            if test_tipi != "Harf":
                st.divider()
                st.subheader("📚 Klasik Norm Referans Tablosu (1. Sınıf Sınır Değerleri)")
                referans_data = {
                    "Yaş Grubu": ["66-71 Ay", "72-77 Ay", "78-83 Ay"] * 3,
                    "Test": ["Şekil"]*3 + ["Renk"]*3 + ["Sayı"]*3,
                    "Çok İyi": ["< 48.9", "< 48.6", "< 48.4", "< 46.8", "< 48.0", "< 44.6", "< 37.0", "< 40.4", "< 36.1"],
                    "İyi": ["48.9-62.2", "48.6-62.0", "48.4-60.7", "46.8-72.7", "48.0-69.0", "44.6-67.4", "37.0-57.1", "40.4-57.6", "36.1-53.7"],
                    "Normal": ["62.2-75.5", "62.0-75.4", "60.7-73.0", "72.7-98.6", "69.0-90.1", "67.4-90.1", "57.1-77.2", "57.6-74.8", "53.7-71.3"],
                    "Zayıf": ["75.5-88.7", "75.4-88.9", "73.0-85.2", "98.6-124.6", "90.1-111.1", "90.1-112.9", "77.2-97.3", "74.8-92.0", "71.3-88.9"],
                    "Çok Zayıf": ["> 88.7", "> 88.9", "> 85.2", "> 124.6", "> 111.1", "> 112.9", "> 97.3", "> 92.0", "> 88.9"]
                }
                st.dataframe(pd.DataFrame(referans_data), use_container_width=True, hide_index=True)

            # --- 9. KURUMSAL LOGO ENTEGRASYONU ---
            st.write("") 
            st.divider()
            _, l_col1, l_col2, l_col3, _ = st.columns([1, 2, 2, 2, 1])

            with l_col1:
                if os.path.exists("hacettepe.svg"): st.image("hacettepe.svg", width=85)
            with l_col2:
                if os.path.exists("duzce.svg"): st.image("duzce.svg", width=140)
            with l_col3:
                if os.path.exists("Rlogo.svg"): st.image("Rlogo.svg", width=120)

            # --- 10. METODOLOJİK ATIF KATMANI ---
            st.write("") 
            st.markdown("<div style='text-align: center; color: gray; font-size: 0.85rem;'>Bu normlama sistemi, Lenhard, Lenhard & Maurice (2018) tarafından R Statistics için geliştirilen cNORM paketi ile sürekli normlama modellemesi (Taylor Polinomu $k=2$) kullanılarak yapılandırılmıştır.</div>", unsafe_allow_html=True)
        else:
            st.warning("Seçilen yaş segmenti için sistemde eşleşen norm verisi üretilemedi.")
