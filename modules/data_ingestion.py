import os
import logging
import numpy as np
from astropy.io import fits
import shutil
import tarfile
from datetime import datetime
from .module import Module

BASE_DIR = "/path/to/base"
DELIVERIES_DIR = os.path.join(BASE_DIR, "deliveries")
SPECTRA_DIR = os.path.join(BASE_DIR, "spectra")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")

class DataIngestion(Module):
    def __init__(self, config):
        self.config = config

    def process_night(self, night):
        night_dir = os.path.join(self.config['deliveries_dir'], night)
        spectra_night_dir = os.path.join(self.config['spectra_dir'], night)
        archive_night_dir = os.path.join(self.config['archive_dir'], night)

        if not os.path.exists(night_dir):
            self.logger.info(f"No data found for night {night}.")
            return

        files = [f for f in os.listdir(night_dir) if f.endswith(".fits")]
        if not files:
            self.logger.info(f"No new files found for night {night}.")
            return

        if not os.path.exists(spectra_night_dir):
            os.makedirs(spectra_night_dir)

        # Write "FALSE" to DONE.txt at the start
        signal_file = os.path.join(spectra_night_dir, "DONE.txt")
        with open(signal_file, 'w') as f:
            f.write("FALSE\n")

        obj_names = []
        for file in files:
            file_path = os.path.join(night_dir, file)
            self.logger.info(f"Processing file: {file}")
            try:
                obj_names.extend(self.process_file(file_path, spectra_night_dir))
            except Exception as e:
                self.logger.error(f"Error processing {file}: {e}")

        self.archive_files(night_dir, archive_night_dir)
        self.set_done(True)
        return obj_names

    def process_file(self, file_path, spectra_night_dir):
        self.logger.info(f"Parsing data from {file_path}")
        obj_names = []
        with fits.open(file_path, memmap=False) as hdulist:
            fibinfodat = hdulist['FIBMETATAB'].data
            specdata = hdulist[2].data
            specheader = hdulist[2].header
            wave = specheader['1CRVL1'] + (1 + np.arange(0, float(specheader['TDIM1'].strip(' ').strip('(').strip(')')))) - specheader['1CRPX1'] * specheader['1CDLT1']
            
            for counter, (flux, fluxerr, qual) in enumerate(zip(specdata['FLUX'], specdata['ERR'], specdata['QUAL'])):
                try:
                    meta = fibinfodat[counter]
                    obj_name = meta['OBJ_NME']
                    obj_names.append(obj_name)
                    
                    spectrum_file = os.path.join(spectra_night_dir, f"{obj_name}_spectrum.txt")
                    metadata_file = os.path.join(spectra_night_dir, f"{obj_name}_metadata.txt")
                    
                    with open(spectrum_file, 'w') as f:
                        f.write("# Wavelength Flux Error Quality\n")
                        for w, fl, fe, q in zip(wave, flux, fluxerr, qual):
                            f.write(f"{w} {fl} {fe} {q}\n")
                    
                    with open(metadata_file, 'w') as f:
                        f.write("# Metadata\n")
                        for name in fibinfodat.names:
                            f.write(f"# {name}: {meta[name]}\n")
                    
                    self.logger.info(f"Saved spectrum to {spectrum_file} and metadata to {metadata_file}")
                except Exception as e:
                    self.logger.error(f"Error processing spectrum {counter} in file {file_path}: {e}")
        return obj_names

    def archive_files(self, night_dir, archive_night_dir):
        if not os.path.exists(archive_night_dir):
            os.makedirs(archive_night_dir)
        
        tar_path = os.path.join(archive_night_dir, f"{os.path.basename(night_dir)}.tar.gz")
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(night_dir, arcname=os.path.basename(night_dir))
        shutil.rmtree(night_dir)
        self.logger.info(f"Archived and removed original data for night {os.path.basename(night_dir)}")

def run(night, logger, config):
    ingestion = DataIngestion(config)
    ingestion.set_logger(logger)
    return ingestion.process_night(night)
