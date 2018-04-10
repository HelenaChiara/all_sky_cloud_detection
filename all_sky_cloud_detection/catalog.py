from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord, AltAz, Angle
import numpy as np
import pandas as pd
from all_sky_cloud_detection.coordinate_transformation import spherical2pixel


def get_catalog(name, mag):
    """This function queries star catalogs from the  VizieR web service.
    Parameters
    -----------
    name: string
            Name of the catalog
    mag: float
        Function selects stars from catalog below given threshold
    Returns
    -------
    ra_catalog: array
                right ascension of the selected catalog stars
    dec_catalog: array
                right ascension of the selected catalog stars
    """
    #Spalten spezifizieren → nur sinnvolle Spalten mitnehmen
    Custom_Vizier = Vizier(columns=['**'])
    Custom_Vizier.ROW_LIMIT = -1
    dat_original = Custom_Vizier.get_catalogs(name)[0]
    dat = dat_original[(dat_original['Vmag'] < mag)]
    ra_catalog = np.array(pd.DataFrame(dat['RA_ICRS_']).dropna())
    dec_catalog = np.array(pd.DataFrame(dat['DE_ICRS_']).dropna())
    return ra_catalog, dec_catalog


def transform_catalog(ra_catalog, dec_catalog, time, cam):
    """This function transforms star coordinates (ra, dec) from a catalog to altaz.
    Parameters
    -----------
    ra_catalog: array
            Name of the catalog
    dec_catalog: array
        Function selects stars from catalog below given threshold
    time: astropy timestamp
            timestamp of the image
    cam: string
        name of the used all sky camera
    Returns
    -------
    pos_altaz: astropy SkyCoord object
                Star positions in altaz at the given time.
    """
    pos = SkyCoord(ra=ra_catalog, dec=dec_catalog, frame='icrs', unit='deg')
    pos_altaz = pos.transform_to(AltAz(obstime=time, location=cam.location))
    return pos_altaz


def match_catalogs(catalog, c, cam):
    """This function compares star positions.
    Parameters
    -----------
    catalog: array
            Stars from a catalog.
    c: array
        Detected stars in an all sky camera image.
    cam: string
        name of the used all sky camera
    Returns
    -------
    c: arrray
        Pixel positions of the matching stars.
    catalog: array
        Pixel positions of the matching stars.
    """
    idxc, idxcatalog, d2d_c, d3d_c = catalog.search_around_sky(c, Angle('1d'))
    matches_catalog = catalog[idxcatalog]
    matches_c = c[idxc]
    catalog_row, catalog_col = spherical2pixel(matches_catalog.alt, matches_catalog.az, cam.lens.theta2r, cam)
    c_row, c_col = spherical2pixel(matches_c.alt, matches_c.az, cam.lens.theta2r, cam)
    catalog_size = np.ones(len(catalog_row))
    c_size = np.ones(len(c_row))
    c = np.array([c_row[0], c_col[0], c_size])
    catalog = np.array([catalog_row[0], catalog_col[0], catalog_size])
    return c, catalog