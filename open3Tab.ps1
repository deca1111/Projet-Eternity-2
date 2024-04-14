# Ouvrir un nouvel onglet dans Windows Terminal Preview avec la commande spécifiée
# Utilisation: open3Tab.ps1 <command>
# Exemple: open3Tab.ps1 "wsl" "wsl" "wsl"

$command = $args
$command = $command -join " ; "

$command = "wt.exe new-tab -p 'Windows PowerShell' -d . ; wt.exe new-tab -p 'Windows PowerShell' -d . ; wt.exe new-tab -p 'Windows PowerShell' -d . ; $command"