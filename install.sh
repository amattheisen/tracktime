echo "Running tracktime installer."
echo "  ...Building."
pyinstaller --onefile --clean tracktime/tracktime.py
if [[ $? -ne 0 ]];then
    echo "  ...Install FAILED - Can't build."
    exit
fi
echo "  ...Build successful."
echo "  ...Coping executable to bin."
sudo cp dist/tracktime /opt/local/bin
if [[ $? -ne 0 ]];then
    echo "  ...Install FAILED - Can't copy."
    exit
fi
echo "  ...Copy successful."
echo "Install successful!"
