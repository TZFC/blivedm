SET /A min = 60
SET /A hour = 60
SET /A halfday = 12
SET /A time = %min%*%hour%*%halfday%
:refresh
start microsoft-edge:"https://account.bilibili.com/account/home"
timeout 60
taskkill /F /IM msedge.exe
timeout %time%
goto refresh