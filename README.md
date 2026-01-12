# Image-Localization

This repository includes the code for the IMPPAIL process as described in Gauld et al. (2025).

The IMPPAIL pipeline is included within the `ImageReg.py` file. Other files are provided to replicate the matching process used for Lunar Trailblazer.

## How to run

Much of the scripts expect to be run from a directory outside of the repository, with folders structured as follows:

```
working-dir/
├── Data_M3/                ## Stores M3 raw data
├── Data_Thermal/
│   ├── DATA                ## Raw simulation outputs as csv
│   ├── TIFFs               ## Processed output (see helpers/Process_Thermal.py)
│   └── M3_IMGS             ## Pre-computed M3 radiance averages
├── Topography/             ## Stores LOLA/Kaguya DEM
├── Image-Localization/     ## This repository
├── Results/                ## Results folder to be populated by M3-Hillshade match
│   ├── Worked              ## Must pre-create these three (empty) folders
│   ├── Failed
│   └── Matches     
└── Results-THERMAL         ## Results folder to be populated by thermal match
```

When in the working dir, run the M3-Hillshade match using

`python Image-Localization/src/LTB_FeatureMatch.py -f <m3id list>`

where m3id list is a file with newline-separated M3IDs for matching. For the thermal match, run 

`python Image-Localization/src/FeatureMatch_Thermal.py`

to populate thermal results.

## Environment

To install all dependencies into a conda env, run the following:

`conda create -n imppail_env -c conda-forge python=3.10 numpy pandas matplotlib gdal opencv scikit-image pillow`