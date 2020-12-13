clear
echo updating -- mini-format-pack ankiaddon
7z u mini-format-pack.ankiaddon ../src/* -xr0!__pycache__ -xr!__pycache__
echo done
start mini-format-pack.ankiaddon
exec $SHELL
