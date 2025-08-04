# Ruta de los scripts Python
$transferScript = "C:\Mondayapp\facturasdcm\transferfdcm.py"
$syncScript = "C:\Mondayapp\facturasdcm\sync_scriptfdcm.py"
$logFile = "C:\Logs\facturasdcm.log"
$transferOut = "C:\Logs\transfer_salidafdcm.log"
$transferErr = "C:\Logs\transfer_errorfdcm.log"
$syncOut = "C:\Logs\sync_salidafdcm.log"
$syncErr = "C:\Logs\sync_errorfdcm.log"

# Ruta completa a python.exe (ajusta si usas entorno virtual)
$pythonPath = "python.exe"

# Funcion para escribir logs
function Write-Log {
    param ([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $message" | Out-File -FilePath $logFile -Append
    Write-Host "$timestamp - $message"
}

# Iniciar registro
Write-Log "==== Inicio de la ejecucion automatica ===="

# 1. Ejecutar transferfdcm.py
try {
    Write-Log "Ejecutando transferfdcm.py..."
    $transferProcess = Start-Process -FilePath $pythonPath `
        -ArgumentList $transferScript `
        -RedirectStandardOutput $transferOut `
        -RedirectStandardError $transferErr `
        -Wait -PassThru -NoNewWindow

    if ($transferProcess.ExitCode -eq 0) {
        Write-Log "transferfdcm.py se ejecuto correctamente (ExitCode: 0)."
    } else {
        Write-Log "ERROR: transferfdcm.py fallo (ExitCode: $($transferProcess.ExitCode))."
        exit 1
    }
} catch {
    Write-Log "ERROR al ejecutar transferfdcm.py: $_"
    exit 1
}

# 2. Esperar 60 segundos antes de ejecutar sync_scriptfdcm.py
Write-Log "Esperando 60 segundos antes de ejecutar sync_scriptfdcm.py..."
Start-Sleep -Seconds 60

# 3. Ejecutar sync_scriptfdcm.py
try {
    Write-Log "Ejecutando sync_scriptfdcm.py..."
    $syncProcess = Start-Process -FilePath $pythonPath `
        -ArgumentList $syncScript `
        -RedirectStandardOutput $syncOut `
        -RedirectStandardError $syncErr `
        -Wait -PassThru -NoNewWindow

    if ($syncProcess.ExitCode -eq 0) {
        Write-Log "sync_scriptfdcm.py se ejecuto correctamente (ExitCode: 0)."
    } else {
        Write-Log "ERROR: sync_scriptfdcm.py fallo (ExitCode: $($syncProcess.ExitCode))."
        exit 1
    }
} catch {
    Write-Log "ERROR al ejecutar sync_scriptfdcm.py: $_"
    exit 1
}

Write-Log "==== Ejecucion completada ===="
