# Uses the ImageReg module to perform feature matching between thermal images 
# and M3 images. This requires the thermal images to be pre-computed and stored
# as TIFF files, and the M3 radiance images to be pre-processed as done in
# the M3 feature matching step (averaged across bands, converted to byte scale).

# Kevin Gauld 2025

import glob, os
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from ImageReg import IMPPAIL

# Choose one of these to use for matching
m3idA = 'M3G20081119T021733'
m3idB = 'M3G20090212T082712'
m3idC = 'M3G20090212T203719'
m3idD = 'M3G20090423T231946'

SCALE_FACTOR = 140/60 # Scale to 140 m/pix to match M3

def make_output_img(therm_img, vswir_img, H_f, kp_f, kp2, matches_f, mask, outfn):
    scale = vswir_img.shape[0]/therm_img.shape[0]
    rs_therm=cv.resize(therm_img, (int(therm_img.shape[1]*scale), vswir_img.shape[0]))

    kpscaled = [cv.KeyPoint(kp.pt[0] * scale, kp.pt[1] * scale, kp.size * scale,
                                      kp.angle, kp.response, kp.octave, kp.class_id)
                         for kp in kp_f]


    # Prepare matchesMask (1 for inliers, 0 for outliers)
    matchesMask = mask.ravel().tolist()

    height = max(rs_therm.shape[0], vswir_img.shape[0])
    width = rs_therm.shape[1] + vswir_img.shape[1]
    output_img = np.zeros((height, width, 3), dtype=np.uint8)
    output_img[:, 0:rs_therm.shape[1]] = np.expand_dims(rs_therm, axis=-1)
    output_img[:,rs_therm.shape[1]:rs_therm.shape[1]+vswir_img.shape[1]] = np.expand_dims(vswir_img, axis=-1)

    ## Draw matches with custom colors
    for i, match in enumerate(matches_f):
        pt1 = tuple(map(int, kpscaled[match.queryIdx].pt))
        pt2 = tuple(map(int, kp2[match.trainIdx].pt))
        pt2 = (pt2[0] + rs_therm.shape[1], pt2[1])  # Shift the point for the second image in combined canvas

        # Draw the keypoints and the line between them
        if matchesMask[i]==0:
            color = (0,0,255)
            cv.circle(output_img, pt1, 2, color, -1)
            cv.circle(output_img, pt2, 2, color, -1)
            cv.line(output_img, pt1, pt2, color, 2 if color==(0, 255, 0) else 1)
        elif matchesMask[i]==1:
            color = (0,255,0)
            cv.circle(output_img, pt1, 2, color, -1)
            cv.circle(output_img, pt2, 2, color, -1)
            cv.line(output_img, pt1, pt2, color, 2 if color==(0, 255, 0) else 1)

    cv.imwrite(outfn, output_img)

def make_overlay_img(therm_img, vswir_img, H_f, ofn):
    # Create a blank canvas that's twice the size of vswir_img
    canvas_size = (2 * vswir_img.shape[1], 2 * vswir_img.shape[0])  # (width, height)

    # Compute offset to center vswir_img on the canvas
    offset_x = vswir_img.shape[1] // 2
    offset_y = vswir_img.shape[0] // 2

    # Translation matrix to center vswir_img
    T_center = np.array([
        [1, 0, offset_x],
        [0, 1, offset_y],
        [0, 0, 1]
    ], dtype=np.float32)
    
    print(T_center)

    # Warp vswir_img to the center of the blank canvas
    img_overlay = cv.warpPerspective(vswir_img, T_center, canvas_size)

    # Warp therm_img using the full homography H_f into the same canvas
    img_therm = cv.warpPerspective(therm_img, T_center@H_f, canvas_size) // 2
    img_overlay = img_overlay // 2  # dim vswir_img for blending

    # Combine both images
    blended = cv.add(img_therm, img_overlay)

    # Write output
    cv.imwrite(ofn, blended.astype(np.uint8))

if __name__ == "__main__":
    m3id = m3idD # Change to select which M3ID to use

    dst_fn = f'Results-THERMAL/{m3id}'
    src_fn = f'Data_Thermal/TIFFs/{m3id}'

    os.makedirs(dst_fn, exist_ok=True)

    # Get the thermal images and the pre-computed M3 image used in matching
    # (same averaging across bands as in the original matching)
    thermal_im_fns = glob.glob(f'{src_fn}/*.tif')
    match_im_fn = f'Data_Thermal/M3_IMGS/{m3id}_RDN_average_byte.tif' 

    therm_image = cv.imread(thermal_im_fns[0], cv.IMREAD_ANYDEPTH)
    match_im = cv.imread(match_im_fn, cv.IMREAD_ANYDEPTH)
    
    FM_OBJ = IMPPAIL()
        
    PLOT=False # Change this to true to pre-plot the first thermal and M3 image
    if PLOT:
        print(therm_image.shape)
        print(match_im.shape)

        plt.imshow(therm_image, cmap='inferno')
        plt.colorbar()
        plt.show()

        plt.imshow(match_im, cmap='gray')
        plt.colorbar()
        plt.show()
    

    for t_im_fn in thermal_im_fns:
        t_img = cv.imread(t_im_fn, cv.IMREAD_ANYDEPTH).astype(np.uint8)
        # Compute new size
        new_size = (int(t_img.shape[1] / SCALE_FACTOR), int(t_img.shape[0] / SCALE_FACTOR))
        
        # Downsample image to best match expected pixel scale
        t_img = cv.resize(t_img, new_size, interpolation=cv.INTER_AREA)
        
        print(f"ORIG: {t_img.shape=}\t{match_im.shape=}")
        
        cropsize = (int(match_im.shape[0]*0.95), int(match_im.shape[1]*0.8))
        t_img = t_img[t_img.shape[0]//2-cropsize[0]//2:t_img.shape[0]//2+cropsize[0]//2,
                      t_img.shape[1]//2-cropsize[1]//2:t_img.shape[1]//2+cropsize[1]//2,]
        
        print(f"CROP: {t_img.shape=}\t{match_im.shape=}")

        # Perform matching. If it works, save an image of the tie points and an overlay image
        # of the two images blended. If it fails, write a failure text file.
        try:
            H_f, kp_f, kp2, matches_f, mask = FM_OBJ.iterative_match(t_img, match_im)
            
            print(f'{dst_fn}/{t_im_fn.split("/")[-1].split(".")[0]}.png')
            make_output_img(t_img, match_im, H_f, kp_f, kp2, matches_f, mask, f'{dst_fn}/{t_im_fn.split("/")[-1].split(".")[0]}.png')
            make_overlay_img(t_img, match_im, H_f, f'{dst_fn}/{t_im_fn.split("/")[-1].split(".")[0]}_overlay.png')
        except Exception as e:
            print(e)
            with open(f'{dst_fn}/{t_im_fn.split("/")[-1].split(".")[0]}.txt', "w") as file:
                file.write('FAILURE')



