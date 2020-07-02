#!/bin/bash

OUTPUT="docs/source/examples.rst"
echo "Examples" > $OUTPUT
echo "========" >> $OUTPUT

for f in examples/*.py; do
    filename=${f##*/}
    [ $filename != '__init__.py' ] || continue
    {
        echo $filename
        echo "---------------------------"
        echo ".. literalinclude:: $filename"
        echo "   :language: python"
        echo "   :linenos:"
        echo ""
    } >> $OUTPUT
done
