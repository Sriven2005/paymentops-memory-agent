$ErrorActionPreference = "Stop"

$env:PYTHONUTF8 = "1"
$env:HINDSIGHT_API_LLM_PROVIDER = "none"
$env:HINDSIGHT_API_RETAIN_EXTRACTION_MODE = "chunks"
$env:HINDSIGHT_API_EMBEDDINGS_PROVIDER = "onnx"
$env:HINDSIGHT_API_RERANKER_PROVIDER = "rrf"

Write-Host "Starting Hindsight with persistent local storage and chunk retain mode."
Write-Host "First startup downloads the configured ONNX embedding model."
& .\.venv\Scripts\hindsight-api.exe --host 127.0.0.1 --port 8888
