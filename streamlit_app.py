# -*- coding: utf-8 -*-
"""
INPI - MVP: Mapa de Calor
"""

import json
import streamlit as st
from pathlib import Path
from PIL import Image

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
MANIFEST_PATH = DATA_DIR / "manifest.json"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
QUERY_ORDER = [
    "input_image",
    "lamborghini",
    "maestro",
    "mastercard",
    "olimpiadas",
    "saucony",
]

DISPLAY_NAMES = {
    "input_image": "Bull",
    "lamborghini": "Lamborghini",
    "maestro": "Maestro",
    "mastercard": "Mastercard",
    "olimpiadas": "Olimp\u00edadas",
    "saucony": "Saucony",
    "audi": "Audi",
    "redbull": "Red Bull",
    "brooks": "Brooks",
    "speedo": "Speedo",
    "cirrus": "Cirrus",
}

USE_FG_AS_HEATMAP = {"olimpiadas"}

LEGENDS = {
    "input_image": (
        "Os pontos em comum entre as marcas **Lamborghini**, **Red Bull** e a "
        "marca **Bull** s\u00e3o os touros. O mapa de calor foca nos atributos da "
        "**cabe\u00e7a do touro**, pois \u00e9 o \u00fanico ponto fisiol\u00f3gico em comum entre os 3 "
        "touros, visto que todos possuem tamanhos, cores e poses diferentes."
    ),
    "lamborghini": (
        "Os pontos em comum entre as marcas **Lamborghini**, **Red Bull** e a "
        "marca **Bull** s\u00e3o os touros. O mapa de calor foca nos atributos do "
        "**corpo do touro como um todo**, pois \u00e9 o \u00fanico ponto fisiol\u00f3gico em "
        "comum entre os 3 touros, visto que todos possuem tamanhos, cores e "
        "poses diferentes."
    ),
    "maestro": (
        "O que trouxe a similaridade entre a marca **Maestro** e todas as "
        "outras foi a **interse\u00e7\u00e3o dos c\u00edrculos**, mais do que as cores ou o "
        "tamanho dos c\u00edrculos. Por isso a concentra\u00e7\u00e3o do vermelho est\u00e1 no "
        "ponto de interse\u00e7\u00e3o dos c\u00edrculos."
    ),
    "mastercard": (
        "O que trouxe a similaridade entre a marca **Mastercard** e todas as "
        "outras foi a **interse\u00e7\u00e3o dos c\u00edrculos**, mais do que as cores ou o "
        "tamanho dos c\u00edrculos. Por isso a concentra\u00e7\u00e3o do vermelho est\u00e1 no "
        "ponto de interse\u00e7\u00e3o dos c\u00edrculos."
    ),
    "olimpiadas": (
        "O que trouxe a similaridade entre a marca **Olimp\u00edadas** e todas as "
        "outras foi a **interse\u00e7\u00e3o dos c\u00edrculos**, mais do que as cores ou o "
        "tamanho dos c\u00edrculos. Por isso a concentra\u00e7\u00e3o do vermelho est\u00e1 no "
        "ponto de interse\u00e7\u00e3o dos c\u00edrculos."
    ),
    "saucony": (
        "O vermelho do mapa de calor se concentra no \u00fanico elemento visual em "
        "comum entre a marca **Saucony**, **Brooks** e **Speedo**. Isso indica "
        "que o motivo do score de similaridade entre as imagens \u00e9 esse "
        '"boomerang" do Saucony.'
    ),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@st.cache_data
def load_manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def resolve(path_str: str) -> Path:
    return DATA_DIR / path_str


def blend_images(query_path: Path, heatmap_path: Path, alpha: float) -> Image.Image:
    query = Image.open(query_path).convert("RGBA")
    heat = Image.open(heatmap_path).convert("RGBA")
    if heat.size != query.size:
        heat = heat.resize(query.size, Image.LANCZOS)
    return Image.blend(query, heat, alpha)


def score_color(v: float) -> str:
    if v >= 0.7:
        return "#27ae60"
    if v >= 0.4:
        return "#f39c12"
    return "#e74c3c"


def score_label(v: float) -> str:
    if v >= 0.7:
        return "Alta"
    if v >= 0.4:
        return "M\u00e9dia"
    return "Baixa"


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="INPI \u2014 MVP: Mapa de Calor",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
    .stApp { background-color: #f8f9fc; }
    .block-container { padding-top: 1.2rem; max-width: 1400px; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a237e 0%, #283593 100%);
    }
    [data-testid="stSidebar"] * { color: #e8eaf6 !important; }
    [data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(255,255,255,0.08);
        border-radius: 8px; padding: 8px 12px; margin-bottom: 4px;
        transition: background 0.2s;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255,255,255,0.15);
    }

    .result-card {
        background: white; border: 1px solid #e0e3eb; border-radius: 12px;
        padding: 16px; margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: box-shadow 0.2s, transform 0.15s;
    }
    .result-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }

    .score-badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 4px 14px; border-radius: 20px; font-size: 14px; font-weight: 600;
    }

    .legend-box {
        background: white; border-left: 4px solid #1a237e;
        border-radius: 0 10px 10px 0; padding: 16px 20px;
        margin: 12px 0 20px; font-size: 14px; line-height: 1.7;
        color: #424242; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    .section-header {
        font-size: 13px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.8px; color: #9e9e9e; margin-bottom: 12px;
        padding-bottom: 8px; border-bottom: 2px solid #e0e3eb;
    }

    .query-panel {
        background: white; border-radius: 14px; padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e0e3eb;
    }

    .color-hint {
        display: flex; align-items: center; gap: 8px;
        font-size: 12px; color: #757575; margin: 2px 0;
    }
    .color-dot {
        width: 10px; height: 10px; border-radius: 50%; display: inline-block;
    }

    /* Home page */
    .home-hero {
        text-align: center; padding: 30px 20px 10px;
    }
    .home-hero h1 {
        color: #1a237e; font-size: 32px; margin-bottom: 8px;
    }
    .home-hero p {
        color: #616161; font-size: 16px; max-width: 800px; margin: 0 auto;
        line-height: 1.7;
    }
    .home-section {
        background: white; border-radius: 14px; padding: 28px 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e0e3eb;
        margin-bottom: 20px;
    }
    .home-section h3 {
        color: #1a237e; font-size: 18px; margin-bottom: 12px;
    }
    .home-section p, .home-section li {
        color: #424242; font-size: 14px; line-height: 1.8;
    }
    .home-section ul { padding-left: 20px; }
    .home-section li { margin-bottom: 6px; }
    .highlight-box {
        background: #e8eaf6; border-radius: 10px; padding: 16px 20px;
        margin: 16px 0; font-size: 14px; color: #283593; line-height: 1.7;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
manifest = load_manifest()
queries = [q for q in QUERY_ORDER if q in manifest]

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## MVP: Mapa de Calor")
    st.markdown("---")

    st.markdown(
        '<p style="font-size:11px;text-transform:uppercase;letter-spacing:1px;'
        'opacity:0.6;margin-bottom:6px">Navega\u00e7\u00e3o</p>',
        unsafe_allow_html=True,
    )

    nav_options = ["In\u00edcio"] + [DISPLAY_NAMES.get(q, q) for q in queries]
    selected_nav = st.radio("Menu", nav_options, label_visibility="collapsed")

    st.markdown("---")

    st.markdown(
        """
    <div style="font-size:12px;opacity:0.7;line-height:1.6">
        <b>Como ler o mapa de calor</b><br><br>
        <div class="color-hint">
            <span class="color-dot" style="background:#e74c3c"></span>
            <b>Vermelho</b> \u2014 regi\u00e3o com alta similaridade
        </div>
        <div class="color-hint">
            <span class="color-dot" style="background:#2980b9"></span>
            <b>Azul / Transparente</b> \u2014 regi\u00e3o sem correspond\u00eancia
        </div>
        <br>
        As regi\u00f5es em vermelho indicam os elementos visuais que mais
        contribuem para a similaridade com marcas j\u00e1 registradas.
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        '<div style="font-size:10px;opacity:0.4;text-align:center">Prova de Conceito \u00b7 DINOv3 ViT-H/16+</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------------------------
if selected_nav == "In\u00edcio":
    st.markdown(
        """
    <div class="home-hero">
        <h1>Mapa de Calor para An\u00e1lise de Similaridade Visual</h1>
        <p>
            Uma ferramenta de <b>explicabilidade</b> que permite visualizar
            <b>quais regi\u00f5es</b> de uma marca s\u00e3o respons\u00e1veis pelo score de
            similaridade com marcas j\u00e1 registradas no banco de dados do INPI.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("")

    # --- O que e o Mapa de Calor ---
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
        <div class="home-section">
            <h3>O que \u00e9 o Mapa de Calor?</h3>
            <p>
                O mapa de calor \u00e9 uma t\u00e9cnica de visualiza\u00e7\u00e3o que sobrep\u00f5e
                cores sobre a imagem de uma marca para indicar <b>quais regi\u00f5es</b>
                da imagem mais contribu\u00edram para que ela fosse considerada
                <b>similar</b> a outras marcas do banco de dados.
            </p>
            <div class="highlight-box">
                <b>Vermelho</b> = regi\u00f5es que o modelo identificou como similares
                a elementos de outras marcas.<br>
                <b>Azul / Transparente</b> = regi\u00f5es sem correspond\u00eancia significativa.
            </div>
            <p>
                Ao ajustar a <b>barra de intensidade</b>, \u00e9 poss\u00edvel controlar
                a opacidade do mapa de calor sobre a imagem original, facilitando
                a identifica\u00e7\u00e3o das regi\u00f5es de interesse.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="home-section">
            <h3>Para que serve?</h3>
            <p>O mapa de calor atende dois p\u00fablicos principais:</p>
            <ul>
                <li>
                    <b>Para o solicitante</b> (quem est\u00e1 tentando registrar uma marca):
                    permite visualizar quais elementos visuais da sua marca s\u00e3o
                    similares a marcas j\u00e1 registradas, orientando poss\u00edveis
                    <b>ajustes no design</b> antes de submeter o pedido.
                </li>
                <li>
                    <b>Para o examinador</b> (quem avalia os pedidos no INPI):
                    oferece uma <b>justificativa visual</b> para o score de
                    similaridade retornado pela pipeline, indicando exatamente
                    <b>por que</b> duas marcas foram consideradas similares.
                </li>
            </ul>
            <div class="highlight-box">
                Na pipeline atual, utilizamos o modelo <b>DINOv3</b> para retornar
                as marcas mais similares. O mapa de calor adiciona
                <b>explicabilidade</b>: em vez de apenas dizer que duas marcas
                s\u00e3o similares, ele mostra <b>onde</b> est\u00e1 a similaridade.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    # --- Exemplo com Mastercard ---
    st.markdown(
        """
    <div class="home-section">
        <h3>Exemplo: Marca Mastercard</h3>
        <p>
            Abaixo, vemos a marca <b>Mastercard</b> como exemplo de consulta.
            O mapa de calor revela que a regi\u00e3o de <b>interse\u00e7\u00e3o dos c\u00edrculos</b>
            \u00e9 o principal fator de similaridade com as marcas retornadas
            (Cirrus, Maestro, Audi e Olimp\u00edadas). Isso significa que, mais do que
            as cores ou o tamanho, \u00e9 o <b>padr\u00e3o de c\u00edrculos sobrepostos</b> que o
            modelo identifica como elemento visual em comum.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Show Mastercard example
    mc_data = manifest.get("mastercard", {})
    mc_outputs = mc_data.get("outputs", {})
    mc_neighbors = mc_data.get("neighbors", [])

    if mc_outputs.get("final_overlay"):
        ex_col1, ex_col2 = st.columns([3, 2], gap="large")

        with ex_col1:
            mc_query = resolve(mc_data["image"])
            mc_heat = resolve(mc_outputs["final_overlay"])
            if mc_query.exists() and mc_heat.exists():
                blended = blend_images(mc_query, mc_heat, 0.45)
                st.image(blended, use_column_width=True, caption="Mastercard \u2014 Mapa de calor com intensidade 45%")

        with ex_col2:
            st.markdown(
                """
            <div class="section-header">Marcas similares retornadas</div>
            """,
                unsafe_allow_html=True,
            )
            for nb in mc_neighbors:
                tname = DISPLAY_NAMES.get(nb["target"], nb["target"].replace("_", " ").title())
                pct = int(nb["cls_sim"] * 100)
                color = score_color(nb["cls_sim"])
                lbl = score_label(nb["cls_sim"])
                st.markdown(
                    f'<div class="result-card">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
                    f'<span style="font-size:16px;font-weight:600;color:#212121">{tname}</span>'
                    f'<span class="score-badge" style="background:{color}18;color:{color}">'
                    f"{pct}% \u00b7 {lbl}</span>"
                    f"</div>"
                    f'<div style="background:#f0f1f5;border-radius:6px;height:8px;overflow:hidden">'
                    f'<div style="background:{color};height:100%;width:{pct}%;border-radius:6px"></div>'
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                t_img = resolve(nb["target_image"])
                if t_img.exists():
                    st.image(str(t_img), use_column_width=True)

    st.markdown("")

    st.markdown(
        """
    <div style="text-align:center;padding:20px 0;color:#9e9e9e;font-size:13px">
        Selecione uma marca no menu lateral para explorar os mapas de calor individualmente.
    </div>
    """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# QUERY PAGE
# ---------------------------------------------------------------------------
else:
    selected_key = queries[nav_options.index(selected_nav) - 1]
    data = manifest[selected_key]
    neighbors = data.get("neighbors", [])
    outputs = data.get("outputs", {})
    display_name = DISPLAY_NAMES.get(selected_key, selected_key)

    query_img_path = resolve(data["image"])

    if selected_key in USE_FG_AS_HEATMAP:
        heatmap_path = resolve(outputs.get("fg_overlay", outputs.get("final_overlay", "")))
    else:
        heatmap_path = resolve(outputs.get("final_overlay", ""))

    # Header
    st.markdown(
        f'<h2 style="color:#1a237e;margin-bottom:2px">'
        f"An\u00e1lise: {display_name}</h2>"
        f'<p style="color:#757575;font-size:15px">'
        f"{len(neighbors)} marca(s) similar(es) encontrada(s)</p>",
        unsafe_allow_html=True,
    )

    legend_text = LEGENDS.get(selected_key, "")
    if legend_text:
        st.markdown(f'<div class="legend-box">{legend_text}</div>', unsafe_allow_html=True)

    # Two-column layout
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown(
            '<div class="section-header">Mapa de Calor da Marca</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="query-panel">', unsafe_allow_html=True)

        opacity = st.slider(
            "Intensidade do mapa de calor",
            min_value=0.0,
            max_value=1.0,
            value=0.45,
            step=0.05,
            help="Mova para a esquerda para ver a imagem original. "
            "Mova para a direita para destacar as regi\u00f5es similares.",
        )

        if query_img_path.exists() and heatmap_path.exists():
            blended = blend_images(query_img_path, heatmap_path, opacity)
            st.image(blended, use_column_width=True)
        else:
            st.image(str(query_img_path), use_column_width=True)

        st.markdown(
            f'<p style="text-align:center;font-size:18px;font-weight:600;'
            f'color:#1a237e;margin-top:8px">{display_name}</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(
            f'<div class="section-header">Marcas Similares ({len(neighbors)})</div>',
            unsafe_allow_html=True,
        )

        if not neighbors:
            st.info("Nenhuma marca similar encontrada acima do limite m\u00ednimo.")
        else:
            for nb in neighbors:
                target_name = DISPLAY_NAMES.get(
                    nb["target"],
                    nb["target"].replace("_", " ").title(),
                )
                sim = nb["cls_sim"]
                pct = int(sim * 100)
                color = score_color(sim)
                label = score_label(sim)

                st.markdown(
                    f'<div class="result-card">'
                    f'<div style="display:flex;justify-content:space-between;'
                    f'align-items:center;margin-bottom:8px">'
                    f'<span style="font-size:16px;font-weight:600;color:#212121">'
                    f"{target_name}</span>"
                    f'<span class="score-badge" style="background:{color}18;'
                    f'color:{color}">{pct}% \u00b7 {label}</span>'
                    f"</div>"
                    f'<div style="background:#f0f1f5;border-radius:6px;height:8px;'
                    f'overflow:hidden">'
                    f'<div style="background:{color};height:100%;width:{pct}%;'
                    f'border-radius:6px"></div>'
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                target_img = resolve(nb["target_image"])
                if target_img.exists():
                    st.image(str(target_img), use_column_width=True)
