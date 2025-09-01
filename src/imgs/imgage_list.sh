#!/bin/bash

mapfile -t image_list < <(ls -1)


array_of_images = "["
for i in ${image_list[@]}; do
	array_of_images=${array_of_images}',''"'${i}'"'
done
echo $array_of_images
