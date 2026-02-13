from numpy import genfromtxt
import numpy as np
import glob
import cv2 as cv
import os

## Simulated data is output in csv files-convert to TIFF for processing.

def get_tiffs(src_paths, dst_fpath):
    for src in src_paths:
        img_fns = glob.glob(f"{src}/*.csv")
        print(f"Starting {src}")
        for fn in img_fns:
            im = genfromtxt(fn, delimiter=',')
            
            # Basic removal of dead pixels from the simulated data (NaN or 1000+)
            dead = np.argwhere(np.isnan(im))
            for p in dead:
                im[p[0], p[1]] = im[p[0]+1, p[1]]
            dead = np.argwhere(im > 1000)
            for p in dead:
                im[p[0], p[1]] = im[p[0]+1, p[1]]
                
            # Scale to maximum dynamic range (0-255), clip data above 95th percentile
            print(fn, im.min(), im.max(), im.ptp())
            im = 255*(im-np.min(im))/np.percentile(im,95)
            im = np.clip(im,0,255)
            
            # Write tiff image out
            im = im.astype(np.uint8)
            print(f"TIFFs/{fn[5:].split('.')[0]}.tif")
            cv.imwrite(f"TIFFs/{fn[5:].split('.')[0]}.tif", im)
        print(f"Done with {src}")

if __name__ == "__main__":
    src_paths = glob.glob('DATA/M3G*')
    dst_fpath = 'TIFFs'
    
    for p in [f'{dst_fpath}/'+ k.split('/')[1] for k in src_paths]:
        if not os.path.exists(p):
            os.mkdir(p)

    get_tiffs(src_paths, dst_fpath)