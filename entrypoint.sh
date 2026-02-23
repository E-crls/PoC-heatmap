#!/bin/bash
set -e

# Start Streamlit in background
streamlit run streamlit_app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true &

# Wait for Streamlit to be ready
echo "Aguardando Streamlit iniciar..."
until curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; do
    sleep 1
done
echo "Streamlit rodando em http://localhost:8501"

# Start ngrok if authtoken is provided
if [ -n "$NGROK_AUTHTOKEN" ]; then
    ngrok config add-authtoken "$NGROK_AUTHTOKEN"
    echo ""
    echo "============================================"
    echo "  Iniciando ngrok..."
    echo "============================================"
    ngrok http 8501 --log=stdout &
    sleep 3

    # Try to get the public URL from ngrok API
    PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null || echo "")

    echo ""
    echo "============================================"
    if [ -n "$PUBLIC_URL" ]; then
        echo "  LINK PUBLICO: $PUBLIC_URL"
    else
        echo "  ngrok ativo - acesse http://localhost:4040"
        echo "  para ver o link publico"
    fi
    echo "============================================"
    echo ""
else
    echo ""
    echo "============================================"
    echo "  ngrok nao configurado."
    echo "  Para ativar, execute com:"
    echo "  docker run -p 8501:8501 -e NGROK_AUTHTOKEN=seu_token inpi-heatmap"
    echo "============================================"
    echo ""
fi

# Keep container alive
wait
