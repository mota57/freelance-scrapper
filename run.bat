@echo off
cd client
start npm run dev
set port_numb=5000
cd ..
start backend\venv\Scripts\activate.bat %port_numb%