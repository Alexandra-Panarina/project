#!/bin/bash
INPUT_DIR=$1
OUTPUT_DIR=$2

parse(){
	EXT=$1
	for i in $(ls ${INPUT_DIR} | grep $EXT); do
		name=$(echo ${i} | sed "s/\.${EXT}//g" | sed 's/\n//g')
		echo ${name}.${EXT}
	done
}

detect_lastnum(){
	last_num=$(ls $OUTPUT_DIR | sed 's/.xml//g' | sed 's/.png//g' | sort -n | tail -n 1)
	echo $last_num
}

init(){
	count_xml=$(ls ${OUTPUT_DIR} | grep xml | wc -l)
	count_png=$(ls ${OUTPUT_DIR} | grep png | wc -l)
	[[ $count_png -ne $count_xml ]] && exit 1 && echo "XML count is neq to PNG"
}

init

last_num=$(detect_lastnum)


let count=${last_num}

for j in $(parse png); do
	let count=count+1
	cp ${INPUT_DIR}/${j} ${OUTPUT_DIR}/${count}.png
done

let count=${last_num}
for j in $(parse xml); do
	let count=count+1
	cp ${INPUT_DIR}/${j} ${OUTPUT_DIR}/${count}.xml
done
