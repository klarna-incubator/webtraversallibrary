#!/bin/bash

OUTPUT="docs/examples.rst"
echo "Examples" > $OUTPUT
echo "========" >> $OUTPUT

for f in `ls examples/*.py`; do
    filename=${f##*/}
    [ $filename != '__init__.py' ] || continue
    {
        echo $filename
        echo "---------------------------"
        echo ".. literalinclude:: ../examples/"$filename
        echo "   :language: python"
        echo "   :linenos:"
        echo ""
    } >> $OUTPUT
done
