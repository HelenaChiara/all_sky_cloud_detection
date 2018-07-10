import astropy.units as u
from astropy.coordinates import Angle
from all_sky_cloud_detection.coordinate_transformation import pixel2horizontal
from astropy.coordinates import SkyCoord


def limit_zenith_angle(row, col, cam, angle, time):
    """This function limits the zenith angle and thus the number of stars used
     in the calculation of cloud cover. If the angle is set to 20 degrees,
     the stars used in the calculation are in a zenith angle range of 0 to 80
     degrees.
    Parameters
    -----------
    row: array
        pixel positions, y axis
    col: array
        pixel positions, x axis
    cam: string
        name of the used all sky camera
    angle: float
            limitation of the zenith angle
    time: astropy timestamp
            timestamp of the used image

    Returns
    -------
    c: array of skycoord objects
        azimuth and altitude of the remaining bright blobs
    """
    observer = cam.location
    time = time
    r, phi, theta = pixel2horizontal(row, col, cam)
    angle = Angle(angle*u.deg)
    theta_new = theta[theta > (angle)]
    phi_new = phi[theta > (angle)]
    c = SkyCoord(
        az=phi_new,
        alt=theta_new,
        frame='altaz',
        obstime=time,
        location=observer
        )
    return c