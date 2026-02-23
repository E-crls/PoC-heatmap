# INPI — MVP: Mapa de Calor para Análise de Similaridade Visual

Aplicação Streamlit que visualiza **mapas de calor** sobre logotipos de marcas, evidenciando quais regiões visuais são responsáveis pelo score de similaridade com marcas já registradas no banco de dados do INPI.

![Python 3.11](https://img.shields.io/badge/python-3.11-blue)
![Streamlit](https://img.shields.io/badge/streamlit-%E2%89%A51.38-red)
![DINOv3](https://img.shields.io/badge/modelo-DINOv3%20ViT--H%2F16%2B-green)

---

## Visão Geral

Este MVP é uma **prova de conceito** que demonstra como técnicas de explicabilidade baseadas no modelo **DINOv3** (ViT-H/16+) podem auxiliar na análise de similaridade visual de marcas.

### O que faz

- Exibe mapas de calor sobrepostos a logotipos, indicando as regiões que mais contribuem para a similaridade com outras marcas.
- Apresenta as marcas similares ranqueadas com score de similaridade visual.
- Permite ajustar a intensidade (opacidade) do mapa de calor sobre a imagem original via slider interativo.

### Para quem

| Público | Benefício |
|---------|-----------|
| **Solicitante** | Visualiza quais elementos visuais de sua marca são similares a marcas já registradas, orientando ajustes no design antes de submeter o pedido. |
| **Examinador** | Recebe justificativa visual para o score de similaridade, indicando exatamente *por que* duas marcas foram consideradas similares. |

---

## Estrutura do Projeto

```
app/
├── streamlit_app.py        # Aplicação Streamlit (interface completa)
├── Dockerfile              # Container Docker com Streamlit + ngrok
├── entrypoint.sh           # Script de inicialização do container
├── requirements.txt        # Dependências Python (streamlit>=1.38.0)
├── .dockerignore            
├── .streamlit/
│   └── config.toml         # Configuração de tema (light)
└── data/
    ├── manifest.json        # Metadados: queries, vizinhos, scores, caminhos
    ├── images/              # 14 logotipos (PNG) do dataset
    │   ├── mastercard.png
    │   ├── lamborghini.png
    │   ├── olimpiadas.png
    │   └── ...
    └── outputs/             # Resultados pré-computados por marca
        ├── mastercard/
        │   ├── final_overlay.png
        │   ├── fg_overlay.png
        │   └── ...
        └── ...
```

> **Nota:** Esta aplicação apenas **visualiza** resultados pré-computados. Não executa inferência do modelo DINOv3 em tempo real.

---

## Marcas Analisadas (Queries)

| Query | Display Name | Descrição do Mapa de Calor |
|-------|-------------|----------------------------|
| `input_image` | Bull | Foco na cabeça do touro — ponto em comum com Lamborghini e Red Bull |
| `lamborghini` | Lamborghini | Foco no corpo do touro como um todo |
| `maestro` | Maestro | Foco na interseção dos círculos |
| `mastercard` | Mastercard | Foco na interseção dos círculos |
| `olimpiadas` | Olimpíadas | Foco na interseção dos círculos (usa foreground mask) |
| `saucony` | Saucony | Foco no elemento "boomerang" — ponto em comum com Brooks e Speedo |

---

## Execução Local

### Pré-requisitos

- Python 3.11+
- pip

### Instalação e execução

```bash
cd app
pip install -r requirements.txt
streamlit run streamlit_app.py --server.headless true
```

A aplicação estará disponível em **http://localhost:8501**.

---

## Execução com Docker

### Build da imagem

```bash
cd app
docker build -t inpi-heatmap .
```

### Execução local (sem ngrok)

```bash
docker run -p 8501:8501 inpi-heatmap
```

Acesse **http://localhost:8501**.

### Execução com link público (ngrok)

Para expor a aplicação via URL pública usando [ngrok](https://ngrok.com/):

```bash
docker run -p 8501:8501 -p 4040:4040 \
  -e NGROK_AUTHTOKEN=seu_authtoken_aqui \
  inpi-heatmap
```

O container irá:
1. Iniciar o Streamlit na porta 8501
2. Aguardar o health check confirmar que está rodando
3. Configurar e iniciar o ngrok automaticamente
4. Imprimir o **link público** no log do container

O painel do ngrok fica disponível em **http://localhost:4040**.

### Exportar imagem para outra máquina

```bash
# Na máquina de origem
docker save inpi-heatmap -o inpi-heatmap.tar

# Na máquina de destino
docker load -i inpi-heatmap.tar
docker run -p 8501:8501 inpi-heatmap
```

---

## Arquitetura Técnica

### Pipeline de Geração (pré-processamento)

Os dados exibidos pela aplicação são gerados por uma pipeline de 4 etapas (localizada em `../scripts/`):

| Etapa | Script | Descrição |
|-------|--------|-----------|
| 1 | `step1_extract_embeddings.py` | Extrai embeddings DINOv3 (CLS + patches) de cada imagem |
| 2 | `step2_compute_similarity.py` | Calcula similaridade CLS entre todas as imagens e ranqueia vizinhos |
| 3 | `step3_alt2.py` | Gera mapas de calor com foreground mask + softmax pooling |
| 4 | `step4_build_html.py` | Compila os resultados em manifesto JSON e assets |

### Modelo

- **DINOv3 ViT-H/16+** (`facebook/dinov3-vith16plus-pretrain-lvd1689m`)
- Hidden size: 1280
- Patch size: 16 × 16 (196 patches por imagem 224×224)
- 4 register tokens

### Técnica de Heatmap (step3_alt2)

1. **Foreground mask**: calcula similaridade cosseno entre o token CLS e cada patch da query para isolar a região de interesse (foreground) da imagem.
2. **Softmax pooling**: para cada patch da query no foreground, calcula similaridade com todos os patches do alvo, aplica softmax (temperatura 0.07) e agrega os top-50 valores.
3. **Agregação CLS-weighted**: pondera os scores de vizinhança pelo score CLS global.
4. **Visualização**: normaliza por percentis (p85–p99) e aplica colormap `jet`.

---

## Configuração do Tema

O tema visual é definido em `.streamlit/config.toml`:

- Tema claro (light) com paleta azul marinho (`#1a237e`)
- Sidebar com gradiente azul escuro
- Cards com sombras suaves e hover effects
- Header, footer e menu do Streamlit ocultados via CSS

---

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `NGROK_AUTHTOKEN` | Não | Token de autenticação do ngrok. Se fornecida, o container inicia automaticamente um túnel público. |

---

## Tecnologias

- **[Streamlit](https://streamlit.io/)** — Framework de visualização interativa
- **[DINOv3](https://huggingface.co/facebook/dinov3-vith16plus-pretrain-lvd1689m)** — Modelo de visão auto-supervisionada (ViT-H/16+)
- **[Pillow](https://pillow.readthedocs.io/)** — Blending de imagens (query + heatmap)
- **[ngrok](https://ngrok.com/)** — Túnel para exposição pública
- **[Docker](https://www.docker.com/)** — Containerização da aplicação
