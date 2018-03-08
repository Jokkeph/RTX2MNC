#!/usr/bin/env python
import dicom, os, argparse, cv2
import numpy as np
import matplotlib.pyplot as plt
import pyminc.volumes.volumes as pyvolume
import pyminc.volumes.factory as pyminc
from matplotlib.path import Path

#Parser section
parser = argparse.ArgumentParser(description='RTX2MNC.')
parser.add_argument('RTX', help='Path to the DICOM RTX file')
parser.add_argument('MINC', help='Path to the MINC container file')
parser.add_argument('RTMINC', help='Path to the OUTPUT MINC RT file')
parser.add_argument("--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()

def pyrtx2mnc():
	#Read dicom rt structure file with pydicom
	RTSS = dicom.read_file(args.RTX)
	if args.verbose:
		print "Regions found: {}".format(RTSS.StructureSetROISequence[0].ROIName)
	#Fetch the minc volume from the input
	volume = pyminc.volumeFromFile(args.MINC)
	#For every ROI encountered create a seperate mapping and file.
	for ROI_id,ROI in enumerate(RTSS.ROIContourSequence):

		# Create one MNC output file per ROI
		RTMINC_outname = args.RTMINC if len(RTSS.ROIContourSequence) == 1 else args.RTMINC[:-4] + "_" + str(ROI_id) + ".mnc"
		#Create volume like the minc file and name it RTMINC_outname
		RTMINC = pyminc.volumeLikeFile(args.MINC,RTMINC_outname)
		contour_sequences = ROI.ContourSequence
		if args.verbose:
			print " --> Found",len(contour_sequences),"contour sequences for ROI:",RTSS.StructureSetROISequence[ROI_id].ROIName
		#For each contoursequence convert world coordinates, draw the contour, check if the drawn points are inside a voxel center grid
		for contour in contour_sequences:
			#Raise error if we do not have a CLOSED_PLANAR type.
			assert contour.ContourGeometricType == "CLOSED_PLANAR"

			if args.verbose:
				print "\t",contour.ContourNumber,"contains",contour.NumberOfContourPoints

			#Convert contourdata to numpy array and reshape as xyz coloumns
			world_coordinate_points = np.array(contour.ContourData).reshape((contour.NumberOfContourPoints,3))
			#Create empty 2d slice(array) with the original slice dimensions
			current_slice = np.zeros((volume.getSizes()[1],volume.getSizes()[2]))
			current_slice_inner = np.zeros((volume.getSizes()[1],volume.getSizes()[2]),dtype=np.float)
			#Create empty 2d array of size of the x,y coordinates
			voxel_coordinates_inplane = np.zeros((len(world_coordinate_points),2))
			current_slice_i = 0
			#Convert world to voxel and set current_slice to the z space or slice number add x,y coordinates to the voxel_coordinates_inplane
			for wi,world in enumerate(world_coordinate_points):
				voxel = volume.convertWorldToVoxel([-world[0],-world[1],world[2]])
				current_slice_i = voxel[0]
				voxel_coordinates_inplane[wi,:] = [voxel[2],voxel[1]]
			#Round x,y coordinates and convert to array again
			converted_voxel_coordinates_inplane = np.array(np.round(voxel_coordinates_inplane),np.int32)
			#Fill the contour place result in image current_slice_inner array
			cv2.fillPoly(current_slice_inner,pts=[converted_voxel_coordinates_inplane],color=1)
			#only return the two tuples that are not zero convert to array and transpose them
			points = np.array(np.nonzero(current_slice_inner)).T
			#Path converts the inplane voxels to a path class with callable values such as contains_points and more(https://matplotlib.org/api/path_api.html)
			p = Path(voxel_coordinates_inplane)
			#Create np.array of True or false values if the points are in the path
			grid = p.contains_points(points[:,[1,0]])

			for pi,point in enumerate(points):
				if not grid[pi]:
					# REMOVE EDGE POINT BECAUSE CENTER IS NOT INCLUDED
					current_slice_inner[point[0],point[1]] = 0

			#Only change the data structure inside the minc volume created earlier
			RTMINC.data[np.int(current_slice_i)] += current_slice_inner


		# Remove even areas - implies a hole.
		RTMINC.data[RTMINC.data % 2 == 0] = 0
		#Write and close file
		RTMINC.writeFile()
		RTMINC.closeVolume()
		#Copy the name of the RTstruct (defined in Mirada) to the name of the MNC file
		if args.verbose:
			print 'minc_modify_header -sinsert dicom_0x0008:el_0x103e="'+RTSS.StructureSetROISequence[ROI_id].ROIName+'" '+RTMINC_outname
		os.system('minc_modify_header -sinsert dicom_0x0008:el_0x103e="'+RTSS.StructureSetROISequence[ROI_id].ROIName+'" '+RTMINC_outname)

	volume.closeVolume()

pyrtx2mnc()
