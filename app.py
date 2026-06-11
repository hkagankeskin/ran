import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="RAN Analytics", layout="wide")

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
                st.error("❌ Hatalı şifre.")
    return False

MODEL_SINIRLARI = {
    "Şekil": {"raw_min": 30.0,  "raw_max": 104.0, "yas_min": 70, "yas_max": 96},
    "Renk":  {"raw_min": 32.0,  "raw_max": 183.0, "yas_min": 70, "yas_max": 96},
    "Sayı":  {"raw_min": 25.0,  "raw_max": 111.0, "yas_min": 70, "yas_max": 96},
    "Harf":  {"raw_min": 19.0,  "raw_max": 64.0,  "yas_min": 83, "yas_max": 96},
}

def bant_goster(t_puani):
    """Persentil bant göstergesi — görsel çubuk"""
    if t_puani <= 30:
        bant = "Çok Zayıf"; renk = "#ef4444"; dolu = 1
    elif t_puani <= 40:
        bant = "Zayıf"; renk = "#f97316"; dolu = 2
    elif t_puani <= 60:
        bant = "Normal"; renk = "#3b82f6"; dolu = 3
    elif t_puani <= 70:
        bant = "İyi"; renk = "#22c55e"; dolu = 4
    else:
        bant = "Çok İyi"; renk = "#16a34a"; dolu = 5

    kareler = ""
    for i in range(1, 6):
        if i <= dolu:
            kareler += f"<span style='background:{renk}; color:white; padding:2px 8px; margin:1px; border-radius:3px; font-size:0.8rem;'>■</span>"
        else:
            kareler += f"<span style='background:#e2e8f0; color:#e2e8f0; padding:2px 8px; margin:1px; border-radius:3px; font-size:0.8rem;'>■</span>"

    return f"{kareler} <span style='font-weight:600; color:{renk};'>{bant}</span>"

def sonuc_hesapla(df, yas_ay, ham_sure):
    """Verilen yaş ve süre için norm sonucunu döndür"""
    df_yas = df[df['Aylik_Yas'] == yas_ay].copy()
    if df_yas.empty:
        return None
    df_yas['raw_numeric'] = pd.to_numeric(df_yas['raw'], errors='coerce')
    idx = (df_yas['raw_numeric'] - ham_sure).abs().idxmin()
    satir = df_yas.loc[idx]
    return {"t": satir['norm'], "p": satir['percentile']}

def klinik_yorum_uret(sonuclar, yas_ay, aktif_testler):
    """Öğretmen için Türkçe klinik yorum üret"""
    sinif = "1. sınıf" if yas_ay <= 82 else "2. sınıf"

    # Performans kategorileri
    zayif = []
    normal = []
    iyi = []

    for test in aktif_testler:
        s = sonuclar.get(test)
        if s is None:
            continue
        if s["t"] <= 40:
            zayif.append(test)
        elif s["t"] <= 60:
            normal.append(test)
        else:
            iyi.append(test)

    satirlar = []

    # Genel giriş
    satirlar.append(f"Öğrenci, {yas_ay} aylık ({sinif}) norm grubu baz alınarak değerlendirilmiştir.")

    # Güçlü alanlar
    if iyi:
        satirlar.append(
            f"**Güçlü alanlar:** {', '.join(iyi)} testlerinde akranlarının üzerinde "
            f"bir otomatizasyon hızı sergilemiştir."
        )

    # Normal alanlar
    if normal:
        satirlar.append(
            f"**Beklenen düzey:** {', '.join(normal)} testlerinde yaşıtlarıyla "
            f"uyumlu bir performans göstermiştir."
        )

    # Zayıf alanlar
    if zayif:
        satirlar.append(
            f"**Dikkat gerektiren alanlar:** {', '.join(zayif)} testlerinde akranlarına "
            f"kıyasla yavaş bir otomatizasyon hızı gözlemlenmiştir. "
            f"Bu durum okuma güçlüğü riskine işaret edebilir; "
            f"uzman değerlendirmesi önerilir."
        )

    # Tüm testler normal veya iyi ise
    if not zayif:
        satirlar.append(
            "Genel değerlendirmede öğrencinin RAN performansı yaş düzeyiyle uyumludur. "
            "Herhangi bir müdahale planlamasına gerek görülmemektedir."
        )

    return "\n\n".join(satirlar)

if check_password():
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; }
        .header-container { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
        .header-logo { height: 60px; border-radius: 8px; }
        h1 { color: #1e3a8a !important; font-family: 'Inter', sans-serif; font-weight: 700; margin: 0; }
        [data-testid="stMetricValue"] { color: #2563eb !important; font-size: 1.8rem !important; }
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
        # --- YAN PANEL ---
        st.sidebar.subheader("⚙️ Parametreler")

        yas_ay = st.sidebar.slider("Öğrenci Yaşı (Ay)", 70, 96, 78)

        st.sidebar.divider()
        st.sidebar.subheader("⏱️ Test Süreleri (Saniye)")
        st.sidebar.caption("Uygulanmayan test için 0 girin.")

        sure_sekil = st.sidebar.number_input("Şekil", min_value=0.0, max_value=300.0, value=0.0, step=0.5)
        sure_renk  = st.sidebar.number_input("Renk",  min_value=0.0, max_value=300.0, value=0.0, step=0.5)
        sure_sayi  = st.sidebar.number_input("Sayı",  min_value=0.0, max_value=300.0, value=0.0, step=0.5)

        # Harf sadece 83+ ay için
        if yas_ay >= 83:
            sure_harf = st.sidebar.number_input("Harf", min_value=0.0, max_value=300.0, value=0.0, step=0.5)
        else:
            sure_harf = 0.0
            st.sidebar.caption("ℹ️ Harf testi 83 ay ve üzeri için uygulanır.")

        sureler = {"Şekil": sure_sekil, "Renk": sure_renk, "Sayı": sure_sayi, "Harf": sure_harf}
        aktif_testler = [t for t, s in sureler.items() if s > 0]

        if not aktif_testler:
            st.info("👈 Sol panelden öğrenci yaşını ve test sürelerini girin.")
        else:
            # --- SONUÇLAR ---
            sonuclar = {}
            uyarilar = []

            for test in aktif_testler:
                sinir = MODEL_SINIRLARI[test]
                sure = sureler[test]

                # Yaş uyumu kontrolü
                if yas_ay < sinir["yas_min"] or yas_ay > sinir["yas_max"]:
                    uyarilar.append(f"**{test}:** {yas_ay} ay bu test için norm aralığı dışında.")
                    continue

                # Süre sınır kontrolü
                if sure < sinir["raw_min"]:
                    uyarilar.append(f"**{test}:** {sure} sn model alt sınırının ({sinir['raw_min']:.0f} sn) altında.")
                elif sure > sinir["raw_max"]:
                    uyarilar.append(f"**{test}:** {sure} sn model üst sınırının ({sinir['raw_max']:.0f} sn) üzerinde.")

                s = sonuc_hesapla(norms[test], yas_ay, sure)
                if s:
                    sonuclar[test] = s

            if uyarilar:
                for u in uyarilar:
                    st.warning(u)

            if sonuclar:
                st.divider()
                st.subheader("📊 Test Karşılaştırması")

                # Başlık satırı
                cols = st.columns(len(sonuclar))
                for col, test in zip(cols, sonuclar):
                    col.markdown(f"### {test}")

                # T-skor satırı
                cols = st.columns(len(sonuclar))
                for col, test in zip(cols, sonuclar):
                    col.metric("T-Skoru", f"{sonuclar[test]['t']:.1f}")

                # Persentil satırı
                cols = st.columns(len(sonuclar))
                for col, test in zip(cols, sonuclar):
                    col.metric("Persentil", f"%{sonuclar[test]['p']:.1f}")

                # Bant göstergesi satırı
                cols = st.columns(len(sonuclar))
                for col, test in zip(cols, sonuclar):
                    with col:
                        st.markdown(
                            bant_goster(sonuclar[test]['t']),
                            unsafe_allow_html=True
                        )

                # --- KLİNİK YORUM ---
                st.divider()
                st.subheader("📝 Öğretmen İçin Klinik Değerlendirme")
                yorum = klinik_yorum_uret(sonuclar, yas_ay, list(sonuclar.keys()))
                st.info(yorum)

        # --- LOGOLAR ---
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
            "<div style='text-align: center; color: #374151; font-size: 0.90rem; margin-bottom: 6px;'>"
            "<strong>Proje Ekibi</strong><br>"
            "Prof. Dr. H. Kağan Keskin — Düzce Üniversitesi &nbsp;|&nbsp; "
            "Prof. Dr. Özay Karadağ — Hacettepe Üniversitesi"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='text-align: center; color: gray; font-size: 0.85rem;'>"
            "Bu normlama sistemi, Lenhard, Lenhard & Maurice (2018) tarafından R Statistics için "
            "geliştirilen cNORM paketi ile sürekli normlama modellemesi (Taylor Polinomu $k=2$) "
            "kullanılarak yapılandırılmıştır.</div>",
            unsafe_allow_html=True
        )
