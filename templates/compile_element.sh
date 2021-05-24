export FOLDER="xxxxx"
echo ""
echo "========================================================================="
echo "Building $FOLDER..."
echo "========================================================================="
if [ -d "build" ]; then
    rm -rf build
fi
python $FOLDER/setup.py build_ext --inplace
rm $FOLDER/src/*.c
rm -rf build


