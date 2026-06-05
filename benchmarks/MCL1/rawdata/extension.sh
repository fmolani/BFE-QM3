for file in *.sdf
do
  mv "$file" "${file%.sdf}.mol"
done
