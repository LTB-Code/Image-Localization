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
│   └── TIFFs               ## Processed output (see helpers/Process_Thermal.py)
├── Topography/             ## Stores LOLA/Kaguya DEM
├── Image-Localization/     ## This repository
├── Results/                ## Results folder to be populated by M3-Hillshade match
│   ├── Worked              ## Stores matching outputs for each M3ID match
│   ├── Failed              ## Stores outputs for each M3ID failure
│   ├── Matches             ## Stores successful matches as overlay images
└── └── Thermal             ## Stores thermal matching results
```

When in the working dir, run the M3-Hillshade match using

`python Image-Localization/src/LTB_FeatureMatch.py -f <m3id list>`

where m3id list is a file with newline-separated M3IDs for matching. For the thermal match, run 

`python Image-Localization/src/FeatureMatch_Thermal.py`

to populate thermal results. This assumes the M3-hillshade matches have already been computed

## Outputs

### LTB_FeatureMatch.py -- M3 to Hillshade

The batch matching process between M3 and Hillshade produces three directories - `Results/Worked` ,`Results/Failed`, and `Results/Matches`. It also produces a output log in `Results/runlog.log` and a data logger in `Results/dataout.csv`.

#### Results/Worked and Results/Matches

For every match that works, the following is saved:


| Header 1 | Header 2 | Header 3 |
|---|---|---|
| Row 1, Col 1 | Row 1, Col 2 | Row 1, Col 3 |
| Row 2, Col 1 | Row 2, Col 2 | Row 2, Col 3 |


## Environment

To install all dependencies into a conda env, run the following:

`conda create -n imppail_env -c conda-forge python=3.10 numpy pandas matplotlib gdal opencv scikit-image pillow`

