# Generates either a single mean distance accuracy value, or a CSV file
# with mean distances for multile M3IDs. Hard-coded to look at the Results folder
# for successful M3IDs and their matches

# Kevin Gauld 2025

import numpy as np
import cv2 as cv
import pandas as pd
import sys, os, logging
import argparse

logging.basicConfig(filename='Results/runlog.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logging.getLogger("PIL.TiffImagePlugin").disabled=True

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

logging.info('CHECKING ACCURACY')


def get_mean_dist(m3id):
    if not os.path.isdir(f'Results/Worked/{m3id}'):
        logging.error(f"{m3id} failed")
        return -1
    matches = np.load(f'Results/Worked/{m3id}/{m3id}_MATCHES.npy')
    H, mask = cv.findHomography(matches[0], matches[1], cv.RANSAC, 3)
    if H is None:
        return -1
    
    hpoints_in = matches[0][mask.ravel() == 1]
    hpoints_out = matches[1][mask.ravel() == 1]

    homogeneous_points = np.hstack((hpoints_in, np.ones((len(hpoints_in), 1))))
    transformed_points_homogeneous = H @ homogeneous_points.T
    hpoints_in_tf = (transformed_points_homogeneous[:2, :].T / transformed_points_homogeneous[2, :].reshape(-1, 1))

    d_tf = np.linalg.norm(hpoints_in_tf - hpoints_out, axis=1)
    mean_dist = np.mean(d_tf)
    if np.isnan(mean_dist):
        return -1
    return mean_dist


def show_results():
    acc_df = pd.read_csv('Results/accuracy.csv')
    md = acc_df['MEAN_DIST'].values
    md = md[md>0]
    logging.info(f"Min: {np.min(md)}, Max: {np.max(md)}, Mean: {np.mean(md)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file",
        type=str,
        default='accuracy.csv',
        help="Input file (default: input.txt)"
    )
    args = parser.parse_args()
    fnout = args.file

    if fnout is None:
        if sys.argv[1] == 'show':
            show_results()
        else:
            logging.info(f"Mean Dist for {sys.argv[1]}: {get_mean_dist(sys.argv[1])}")
        quit()
    
    m3ids = open(sys.argv[2], 'r').read().split('\n')

    if fnout not in os.listdir('Results'):
        data = pd.DataFrame(columns=['M3ID', 'MEAN_DIST'])
    else:
        data = pd.read_csv(f'Results/{fnout}')
    
    for k_m3id in range(len(m3ids)):
        logging.info(f"Starting {m3ids[k_m3id]}")
        mdist = get_mean_dist(m3ids[k_m3id])
        k_data = {'M3ID': m3ids[k_m3id], 'MEAN_DIST': mdist}
        data = pd.concat([data, pd.DataFrame(k_data, index=[0])])
        data.to_csv(f'Results/{fnout}',index=False)
    show_results()