import streamlit as st
import pandas as pd
import os

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="RAN Analytics", layout="wide")

# --- 2. ŞİFRE KONTROLÜ ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
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

# --- 3. MODEL SINIRLARI ---
MODEL_SINIRLARI = {
    "Şekil": {"raw_min": 30.0,  "raw_max": 104.0, "yas_min": 70, "yas_max": 96},
    "Renk":  {"raw_min": 32.0,  "raw_max": 183.0, "yas_min": 70, "yas_max": 96},
    "Sayı":  {"raw_min": 25.0,  "raw_max": 111.0, "yas_min": 70, "yas_max": 96},
    "Harf":  {"raw_min": 19.0,  "raw_max": 64.0,  "yas_min": 83, "yas_max": 96},
}

if check_password():
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; }
        .header-container { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
        .header-logo { height: 60px; border-radius: 8px; }
        h1 { color: #1e3a8a !important; font-family: 'Inter', sans-serif; font-weight: 700; margin: 0; }
        [data-testid="stMetricValue"] { color: #2563eb !important; font-size: 1.8rem !important; }
        .stAlert { border-radius: 12px; border: none; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        hr { border-top: 1px solid #cbd5e1 !important; }
        </style>
        """, unsafe_allow_html=True)

    logo_url = "https://support.renaissance.com/servlet/rtaImage?eid=ka0Nx00000073KX&feoid=00NQg000006K5pm&refid=0EMQg00000IutXM"
    st.markdown(f"""
        <div class="header-container">
            <img src="{logo_url}" class="header-logo" alt="RAN Logo">
            <h1>RAN Analytics System</h1>
        </div>
        """, unsafe_allow_html=True)
    st.write("Hızlı Otomatik İsimlendirme (RAN) Klinik Karar Destek Aracı")

    @st.cache_data
    def load_data():
        try:
            return {
                "Şekil": pd.read_csv("RAN_Sekil_Tum_Aylar_Norm_Tablosu.csv"),
                "Renk":  pd.read_csv("RAN_Renk_Tum_Aylar_Norm_Tablosu.csv"),
                "Sayı":  pd.read_csv("RAN_Sayi_Tum_Aylar_Norm_Tablosu.csv"),
                "Harf":  pd.read_csv("RAN_Harf_Tum_Aylar_Norm_Tablosu.csv"),
            }
        except Exception:
            st.error("Sistem Hatası: Norm veritabanı yüklenemedi!")
            return None

    norms = load_data()

    if norms:
        st.sidebar.subheader("⚙️ Parametreler")
        test_tipi = st.sidebar.selectbox("Test Modülü", ["Şekil", "Renk", "Sayı", "Harf"])
        sinir = MODEL_SINIRLARI[test_tipi]

        yas_ay = st.sidebar.slider(
            "Öğrenci Yaşı (Ay)",
            sinir["yas_min"], sinir["yas_max"], sinir["yas_min"]
        )

        st.sidebar.caption(f"📏 Geçerli süre aralığı: **{sinir['raw_min']:.0f} – {sinir['raw_max']:.0f} saniye**")
        ham_sure = st.sidebar.number_input(
            "Tamamlama Süresi (Saniye)",
            min_value=1.0, max_value=300.0,
            value=float(sinir["raw_min"] + (sinir["raw_max"] - sinir["raw_min"]) / 2),
            step=0.5
        )

        sinir_disi = ham_sure < sinir["raw_min"] or ham_sure > sinir["raw_max"]

        if sinir_disi:
            if ham_sure < sinir["raw_min"]:
                st.warning(
                    f"⚠️ Girilen süre ({ham_sure} sn), {test_tipi} testi norm modelinin alt sınırının "
                    f"({sinir['raw_min']:.0f} sn) altındadır. Sonuçlar güvenilir değildir."
                )
            else:
                st.warning(
                    f"⚠️ Girilen süre ({ham_sure} sn), {test_tipi} testi norm modelinin üst sınırının "
                    f"({sinir['raw_max']:.0f} sn) üzerindedir. Sonuçlar güvenilir değildir."
                )

        df_secili = norms[test_tipi]
        df_yas = df_secili[df_secili['Aylik_Yas'] == yas_ay].copy()

        if not df_yas.empty:
            df_yas['raw_numeric'] = pd.to_numeric(df_yas['raw'], errors='coerce')
            idx = (df_yas['raw_numeric'] - ham_sure).abs().idxmin()
            sonuc_satiri = df_yas.loc[idx]
            t_puani = sonuc_satiri['norm']
            yuzdelik = sonuc_satiri['percentile']

            if t_puani <= 30:   durum = "🔴 Kritik: Çok Yavaş Performans"
            elif t_puani <= 40: durum = "🟡 Risk: Yavaş Otomatizasyon"
            elif t_puani >= 60: durum = "🟢 Üstün: Çok Hızlı Otomatizasyon"
            else:               durum = "🔵 Standart: Beklenen Gelişim Seviyesi"

            st.divider()
            st.subheader("📈 Analitik Sonuçlar")
            col1, col2, col3 = st.columns(3)
            col1.metric("T-Skoru", f"{t_puani:.2f}")
            col2.metric("Persentil", f"%{yuzdelik:.1f}")
            col3.metric("Ham Süre", f"{ham_sure} sn")

            guvensizlik = " *(Model sınırı dışı — güvenilirlik düşük)*" if sinir_disi else ""
            st.info(
                f"**{durum}**{guvensizlik}\n\n"
                f"Analiz: {yas_ay} aylık norm grubunda {test_tipi} testi için girilen "
                f"{ham_sure} saniyelik performans, akran popülasyonunun "
                f"%{yuzdelik:.1f}'inden daha efektif bir otomatizasyon hızına işaret eder."
            )

            if test_tipi != "Harf":
                st.divider()
                st.subheader("📚 Klasik Norm Referans Tablosu (1. Sınıf Sınır Değerleri)")
                referans_data = {
                    "Yaş Grubu": ["66-71 Ay", "72-77 Ay", "78-83 Ay"] * 3,
                    "Test": ["Şekil"]*3 + ["Renk"]*3 + ["Sayı"]*3,
                    "Çok İyi":   ["< 48.9", "< 48.6", "< 48.4", "< 46.8", "< 48.0", "< 44.6", "< 37.0", "< 40.4", "< 36.1"],
                    "İyi":       ["48.9-62.2", "48.6-62.0", "48.4-60.7", "46.8-72.7", "48.0-69.0", "44.6-67.4", "37.0-57.1", "40.4-57.6", "36.1-53.7"],
                    "Normal":    ["62.2-75.5", "62.0-75.4", "60.7-73.0", "72.7-98.6", "69.0-90.1", "67.4-90.1", "57.1-77.2", "57.6-74.8", "53.7-71.3"],
                    "Zayıf":     ["75.5-88.7", "75.4-88.9", "73.0-85.2", "98.6-124.6", "90.1-111.1", "90.1-112.9", "77.2-97.3", "74.8-92.0", "71.3-88.9"],
                    "Çok Zayıf": ["> 88.7", "> 88.9", "> 85.2", "> 124.6", "> 111.1", "> 112.9", "> 97.3", "> 92.0", "> 88.9"]
                }
                st.dataframe(pd.DataFrame(referans_data), use_container_width=True, hide_index=True)
        else:
            st.warning("Seçilen yaş segmenti için norm verisi bulunamadı.")

        st.write("")
        st.divider()
        _, l_col1, l_col2, l_col3, _ = st.columns([1, 2, 2, 2, 1])
        with l_col1:
            if os.path.exists("hacettepe.svg"): st.image("hacettepe.svg", width=85)
        with l_col2:
            if os.path.exists("duzce.svg"): st.image("duzce.svg", width=140)
        with l_col3:
            if os.path.exists("Rlogo.svg"): st.image("Rlogo.svg", width=120)

        st.write("")
        st.markdown(
            "<div style='text-align: center; color: gray; font-size: 0.85rem;'>"
            "Bu normlama sistemi, Lenhard, Lenhard & Maurice (2018) tarafından R Statistics için "
            "geliştirilen cNORM paketi ile sürekli normlama modellemesi (Taylor Polinomu $k=2$) "
            "kullanılarak yapılandırılmıştır.</div>",
            unsafe_allow_html=True
        )
