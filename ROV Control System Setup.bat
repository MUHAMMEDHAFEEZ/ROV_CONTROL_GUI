::[Bat To Exe Converter]
::
::fBE1pAF6MU+EWHveyFIiJxFRTxCRAFmVMIo/x8bP3cWrnWoofd4zd4jUlL2NL4A=
::YAwzoRdxOk+EWAjk
::fBw5plQjdC2DJEmW+0g1Kw9HcDatClSZKZso2sfX0M2yi3ERW+UwNobY1dQ=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+IeA==
::cxY6rQJ7JhzQF1fEqQJhZksaHGQ=
::ZQ05rAF9IBncCkqN+0xwdVsFAlTMbAs=
::ZQ05rAF9IAHYFVzEqQICBy0UbwuMKHm1CvUv8fvv6ufHkUgJQfJf
::eg0/rx1wNQPfEVWB+kM9LVsJDDatCiuZCbsI+uf3r9mesVkYWaIMfZvOytQ=
::fBEirQZwNQPfEVWB+kM9LVsJDDatCiuZCbsI+uf3r9mesVkYWaIMfZvOytQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWHGl0mcVEns=
::YQ03rBFzNR3SWATE3GMWDT5uLA==
::dhAmsQZ3MwfNWATE3GMWDT5uLA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdC2DJEmW+0g1Kw9HcDatClSZKZso2sfX0M2yi3Eve9R/W4DVzqaBLKAg81bwcJtt5X9OjdtCCQNdHg==
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
chcp 65001 >nul
title ROV Control System Setup

echo.
echo ========================================
echo    ROV Control System Setup
echo ========================================
echo.

echo This script will check your system and install the necessary requirements for the ROV Control System.
echo Checking system and installing requirements...
python setup.py

echo.
echo Do you want to start the app now? (y/n)
set /p choice="Choose (y/n): "

if /i "%choice%"=="y" (
    echo.
    echo Start ROV Control System...
    python main.py
) else (
    echo.
    echo you can start the app later by running:
    echo python main.py
)

echo.
echo Click any key to exit...
pause >nul
