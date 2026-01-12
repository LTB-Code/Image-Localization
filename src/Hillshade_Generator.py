# Generatees hillshade images from LOLA topography for a given M3 observation
# Uses GDAL DEMProcessing to compute hillshade with given azimuth, incidence angle, and
# z-factor. Clips the global LOLA DEM to the M3 observation bounding box and reprojects
# to sinusoidal projection prior to hillshade generation.

# Kevin Gauld 2025

from osgeo import gdal
import numpy as np
import cv2 as cv

class Hillshade_Generator:
    def __init__(self, M3_OBJ, workdir, inlola="Topography/LunarTopography_60mpx.tif"):
        self.M3_OBJ=M3_OBJ
        self.workdir=workdir
        self.inlola=inlola
        self.get_topo_sinu(regen_topo=True)
    
    def get_topo_clip(self, outfn=None):
        # Clips the global LOLA DEM topography to the bounding box defined by the
        # M3 observation region
        if outfn is None:
            outfn = f'{self.workdir}/{self.M3_OBJ.m3id}_topo.tif'
        
        gdal.Warp(outfn, self.inlola,
                options = gdal.WarpOptions(
                    format='GTiff',
                    outputBounds=(self.M3_OBJ.bound_minlon,
                                self.M3_OBJ.bound_minlat,
                                self.M3_OBJ.bound_maxlon,
                                self.M3_OBJ.bound_maxlat),
                    outputBoundsSRS='+proj=longlat +a=1737400 +b=1737400 +no_defs'
                ))
        self.clip_fn = outfn
    
    def get_topo_sinu(self, outfn=None, regen_topo=False):
        # Reprojects the clipped topography to sinusoidal projection, regenerating
        # the clipped region if needed.

        if outfn is None:
            outfn = f'{self.workdir}/{self.M3_OBJ.m3id}_topo_sinu.tif'
        
        if regen_topo:
            self.get_topo_clip()

        gdal.Warp(outfn,self.clip_fn,
            options=gdal.WarpOptions(
                format='GTiff',
                dstSRS=f'+proj=sinu +lon_0={self.M3_OBJ.clon} +x_0=0 +y_0=0 +a=1737400 +b=1737400 +no_defs'
            ))
        
        self.sinu_fn = outfn
        sinu_img = cv.imread(self.sinu_fn, cv.IMREAD_ANYDEPTH)
        self.sinu_mask = np.where(sinu_img < 32767)
    
    def get_hillshade(self, azm=None, inc=None, zfactor=1, fnout=None, regen_topo=False):
        # Creates the hillshade based on the sinusoidal topography, with the same
        # observation geometry as the M3 observation (azimuth, incidence angle).
        # If desired, a z-factor can be specified to scale the topography.

        azm     = self.M3_OBJ.azm if azm is None else azm
        inc     = self.M3_OBJ.inc if inc is None else inc
        alt     = 90-inc

        if fnout is None:
            fnout = f'{self.workdir}/{self.M3_OBJ.m3id}_hillshade_az{azm:0.2f}_inc{inc:0.2f}_z{zfactor:0.2f}.tif'
        if regen_topo:
            self.get_topo_sinu(regen_topo=True)

        gdal.DEMProcessing(
            fnout, self.sinu_fn, "hillshade",
            options=gdal.DEMProcessingOptions(
                format='GTiff',
                alg='ZevenbergenThorne',
                azimuth=azm,
                altitude=alt,
                zFactor=zfactor
            ))
        return fnout
    
    def get_best_zfactor(self, azm=None, inc=None, initial_guess=1):
        # This function iteratively computes hillshades with different z-factors
        # to find the best z-factor that maximizes contrast in the hillshade image.
        # It does this by analyzing the proportion of high and low saturation pixels,
        # as well as the standard deviation and mean of pixel values in the hillshade
        # within the M3 observation region.
        
        azm     = self.M3_OBJ.azm if azm is None else azm
        inc     = self.M3_OBJ.inc if inc is None else inc
        alt     = 90-inc
        guess = initial_guess

        for i in range(10):
            prev_guess = guess
            hsh_fn = self.get_hillshade(azm=azm, inc=inc, zfactor=guess)
            hsh_image = cv.imread(hsh_fn, cv.IMREAD_ANYDEPTH)
            hsh_masked_region = hsh_image[self.sinu_mask]

            prop_high = len(np.where(hsh_masked_region>250)[0])/len(hsh_masked_region)
            prop_low = len(np.where(hsh_masked_region<5)[0])/len(hsh_masked_region)
            stdev = hsh_masked_region.std()
            mean = hsh_masked_region.mean()
            print(f"high saturation: {prop_high}")
            print(f"low saturation: {prop_low}")
            print(f"standard deviation: {hsh_masked_region.std()}")
            print(f"mean: {hsh_masked_region.mean()}")

            guess += round(prop_high*10)
            guess -= round(prop_low*10)
            if stdev < 45:
                guess += 0.5
            if mean < 100:
                guess -= 1 if mean < 50 else 0.5
            if mean > 150:
                guess += 1 if mean > 200 else 0.5
            if mean-stdev < 0:
                guess -= 1
            if mean+stdev > 255:
                guess += 1
            
            guess = max(0.5, guess)

            print(f"{prev_guess} --> {guess}")
            if guess == prev_guess:
                break
        return guess

