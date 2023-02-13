CALL "%UserProfile%\anaconda3\Scripts\activate.bat" "%UserProfile%\anaconda3\envs\psychopy"
cd %~dp0
python triggertest.py
