# Ruta de los scripts Python
$transferScript = "C:\Mondayapp\facturasdcm\transferdcm.py"
$syncScript = "C:\Mondayapp\facturasdcm\sync_scriptdcm.py"
$logFile = "C:\Logs\facturasfdcm.log"
$transferOut = "C:\Logs\transferfdcm_salida.log"
$transferErr = "C:\Logs\transferfdcm_error.log"
$syncOut = "C:\Logs\syncfdcm_salida.log"
$syncErr = "C:\Logs\syncfdcm_error.log"

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

# 1. Ejecutar transferdcm.py
try {
    Write-Log "Ejecutando transferdcm.py..."
    $transferProcess = Start-Process -FilePath $pythonPath `
        -ArgumentList $transferScript `
        -RedirectStandardOutput $transferOut `
        -RedirectStandardError $transferErr `
        -Wait -PassThru -NoNewWindow

    if ($transferProcess.ExitCode -eq 0) {
        Write-Log "transferdcm.py se ejecuto correctamente (ExitCode: 0)."
    } else {
        Write-Log "ERROR: transferdcm.py fallo (ExitCode: $($transferProcess.ExitCode))."
        exit 1
    }
} catch {
    Write-Log "ERROR al ejecutar transferdcm.py: $_"
    exit 1
}

# 2. Esperar 60 segundos antes de ejecutar sync_scriptdcm.py
Write-Log "Esperando 60 segundos antes de ejecutar sync_scriptdcm.py..."
Start-Sleep -Seconds 60

# 3. Ejecutar sync_scriptdcm.py
try {
    Write-Log "Ejecutando sync_scriptdcm.py..."
    $syncProcess = Start-Process -FilePath $pythonPath `
        -ArgumentList $syncScript `
        -RedirectStandardOutput $syncOut `
        -RedirectStandardError $syncErr `
        -Wait -PassThru -NoNewWindow

    if ($syncProcess.ExitCode -eq 0) {
        Write-Log "sync_script4.py se ejecuto correctamente (ExitCode: 0)."
    } else {
        Write-Log "ERROR: sync_script4.py fallo (ExitCode: $($syncProcess.ExitCode))."
        exit 1
    }
} catch {
    Write-Log "ERROR al ejecutar sync_script4.py: $_"
    exit 1
}

Write-Log "==== Ejecucion completada ===="
