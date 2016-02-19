for FILENAME in `ls *.ui`; do BASENAME=${FILENAME##*/}; pyuic4 $BASENAME > ../src/frame/${BASENAME%.*}.py; done

