# Image Localization: Code for the Iterative Matching Pipeline for Post-Acquisition Image Localization (IMPPAIL)

This repository includes the code for the IMPPAIL process as described in Gauld et al. (2025).

The IMPPAIL pipeline is included within the `ImageReg.py` file. This module is made with the intention of being usable in other similar applications without relying on the Lunar Trailblazer-specific files. Other files are provided to replicate the matching process used for Lunar Trailblazer, and give insight into implementation for potentially desireable matching outputs.

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

where m3id list is a file with newline-separated M3IDs for matching. Alternatively, to run a single m3id, run

`python Image-Localization/src/LTB_FeatureMatch.py <m3id>`

Note that the thermal matching code assumes the M3 matching has been run already. To run the thermal matching there are three options

`python Image-Localization/src/FeatureMatch_Thermal.py -f <m3id list>`
`python Image-Localization/src/FeatureMatch_Thermal.py <m3id>`
`python Image-Localization/src/FeatureMatch_Thermal.py`

where the first two options work the same as for M3 matching. A run with no args will populate all four possible thermal cases.

## Outputs

### LTB_FeatureMatch.py (M3 to Hillshade)

The batch matching process between M3 and Hillshade produces three directories - `Results/Worked` ,`Results/Failed`, and `Results/Matches`. It also produces a output log in `Results/runlog.log` and a data log in `Results/dataout.csv`.

#### Results/Worked and Results/Matches

For every match that works, the following is saved in the `Results/Worked/{m3id}` sub-directory:

| File name | Description |
|---|---|
| `{m3id}_az{azm}_inc{inc}_overlay.tif`| Output overlay image |
| `{m3id}_az{azm}_inc{inc}_pairs.tif`| Output match pairs, drawn from M3 to HSH |
| `{m3id}_az{azm}_inc{inc}_z{zf}` | Hillshade generated for matching. If a z-factor other than 1 is used, both hillshades for the used z factor and 1 are saved. |
| `{m3id}_az{azm}_inc{inc}_NORM`| Normalized hillshade used in matching. Uses the z-factor which successfully matched.|
| `{m3id}_RDN_average_byte.tif` | M3 image from band averaging |
| `{m3id}_RDN_NORM.tif`| Normalized M3 image|
| `{m3id}_HOMOGRAPHY.csv`| 3x3 homography matrix computed from M3 to hillshade |
| `{m3id}_LAT.npy` / `{m3id}_LAT.png` | Latitude backplane as a np array, with png for vis |
| `{m3id}_LON.npy` / `{m3id}_LON.png` | Longitude backplane as a np array, with png for vis |
| `{m3id}_MATCHES.csv` | Correspondence table from pixel in M3 image to pixel in hillshade and corresponding lat/lon.Note a value of 600 in lat/lon is a NODATA value, falling outside the computed backplane.|

In `Results/Matches`, there is a single file for each successful match, `{m3id}_match.tif`, which is a copy of the output overlay image for easy access (also given in `Results/Worked/{m3id}/{m3id}_az{azm}_inc{inc}_overlay.tif`)

#### Results/Failed

There are two cases for `Results/Failed`, with either an inability to find any homography, or a homography that produces an incorrect backplane. The possible outputs are as follows:

| File name | Description | Output condition |
|---|---|---|
| `{m3id}_az{azm}_inc{inc}_overlay.tif`| Output overlay image | Only if backplane error |
| `{m3id}_az{azm}_inc{inc}_pairs.tif`| Output match pairs, drawn from M3 to HSH | Only if backplane error |
| `{m3id}_az{azm}_inc{inc}_z{zf}` | Hillshade generated for matching. If a z-factor other than 1 is used, both hillshades for the used z factor and 1 are saved. | All failures |
| `{m3id}_az{azm}_inc{inc}_NORM`| Normalized hillshade used in matching. Uses the z-factor which successfully matched.| All Failures |
| `{m3id}_RDN_average_byte.tif` | M3 image from band averaging | All Failures |
| `{m3id}_RDN_NORM.tif`| Normalized M3 image| All Failures |
| `{m3id}_HOMOGRAPHY.csv`| 3x3 homography matrix computed from M3 to hillshade | Only if backplane error |
| `{m3id}_LAT.npy` / `{m3id}_LAT.png` | Latitude backplane as a np array, with png for vis | Only if backplane error |
| `{m3id}_LON.npy` / `{m3id}_LON.png` | Longitude backplane as a np array, with png for vis | Only if backplane error |
| `{m3id}_MATCHES.csv` | Correspondence table from pixel in M3 image to pixel in hillshade and corresponding lat/lon. Note a value of 600 in lat/lon is a NODATA value, falling outside the computed backplane.| Only if backplane error |


#### Results/dataout.csv

The output data log stores information on the run and image acquisition. The columns are as follows:

| Column Name | Description |
|---|---|
|M3ID| M3ID for the corresponding entry |
|WORKED| True if the matching worked, else False |
|FIRST_TRY| True if the matching worked on the first z-factor tried, else False |
|FILE_FOUND| True if the M3ID imagery file was found, else False |
|LON| Center longitude of M3 image acquisition from image observation file |
|LAT| Center latitude of M3 image acquisition from image observation file |
|BND_LON_MIN| Minimum longitude of bounding box used to generate the hillshade |
|BND_LON_MAX| Maximum longitude of bounding box used to generate the hillshade |
|BND_LAT_MIN| Minimum latitude of bounding box used to generate the hillshade |
|BND_LAT_MAX| Maximum latitude of bounding box used to generate the hillshade |
|INC| Solar incidence angle of observation |
|AZM| Solar azimuth angle of observation |
|Z_FACTOR| Z-Factor used in matching |
|N_MATCHES| Number of match pairs used in creating the homography, -1 if no match was created |
|MEAN_RADIUS| Mean radial error after applying the homography to the source points, in hillshade-frame pixels. -1 if no match was created.|

### FeatureMatch_Thermal.py (Thermal to M3)

All results for a given m3id run are stored in `Results/Thermal/{m3id}`. Within this directory are two subdirectories: `Worked` and `Failed`. It is important to note that the distinction between worked and failed is strictly if a homography was successfully created, and does not assess the accuracy of the homography itself. That is to say, manual inspection is necessary to verify that results in the `Worked` directory are valid, but results in the `Failed` directly are guaranteed to be unsuccessful.

For the `Worked` directory, we have the following outputs for each local hour `lh`

| File name | Description |
|---|---|---|
| `{m3id}_localhour_{lh}_overlay.tif`| Output overlay image |
| `{m3id}_localhour_{lh}_pairs.tif`| Output match pairs, drawn from Thermal to M3 |
| `{m3id}_HOMOGRAPHY.csv`| 3x3 homography matrix computed from Thermal to M3 |
| `{m3id}_MATCHES.csv` | Correspondence table from pixel in Thermal image to pixel in M3 image. |

For the `Failed` directory, there is a single output for each local hour `lh`.

| File name | Description |
| `{m3id}_localhour_{lh}.txt`.| File containing word 'FAILURE' to denote a failure to create homography |

## Environment

To install all dependencies into a conda env, run the following:

`conda create -n imppail_env -c conda-forge python=3.10 numpy pandas matplotlib gdal opencv scikit-image pillow`

## References

For more information on the algorithm and applications, see 

`Gauld, K.D. et al. (2026), Post-Acquisition Image-Based Localization for High Resolution Thermal and Visible/Shortwave Infrared Images with Application to the Lunar Trailblazer Mission. Earth and Space Science, doi: 10.10/292025EA004594`

Thermal data used in this paper, as well as our results will be in a forthcoming publicly available dataset on CaltechDATA.
