# Cartucheira EDER v0.1

Aplicativo profissional com 36 cartuchos, efeitos incorporados, salvamento automático e backup completo.

## Gerar o executável no Windows 10/11 (64 bits)

1. Instale o Python 3.12 de 64 bits e marque **Add Python to PATH**.
2. Execute `build_windows.bat`.
3. O arquivo independente será criado em `dist\Cartucheira EDER.exe`.

O computador final não precisa ter Python. A programação fica em `%LOCALAPPDATA%\Cartucheira EDER`.

Clique no cartucho para tocar. No botão `⋮`, é possível trocar o áudio, renomear ou limpar. Os backups `.eder` incluem configurações e áudios personalizados.

## Operação profissional

- Atalhos por linha: `1–6`, `Q–Y`, `A–H`, `Z–N`, `F1–F6` e `F7–F12`.
- **Bloquear** protege nomes, cores, áudios e configurações durante a transmissão.
- Um segundo acionamento no mesmo cartucho aplica fade-out e encerra o áudio.
- A saída de som pode ser escolhida na engrenagem.
- A normalização de volume é automática.
- O espectro exibido usa os dados reais do áudio em reprodução.
