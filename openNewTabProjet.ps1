# Ouvrir un nouvel onglet dans Windows Terminal Preview avec la commande spécifiée

# Utilisation: openNewTabProjet.ps1 <command>
# Exemple: openNewTabProjet.ps1 "wsl"

$command = $args
$command = $command -join " ; "

$command = "wt.exe new-tab -p 'Windows PowerShell' -d . ; $command"