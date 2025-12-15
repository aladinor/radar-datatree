import fsspec
import pandas as pd
import xarray as xr
import xradar as xd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta


def rain_depth(z: xr.DataArray, a: float=200.0, b: float=1.6, t: float=None) -> xr.DataArray:
    """
    Estimates rainfall depth using radar reflectivity and Z-R relationship.
    
    Parameters:
    -----------
    z : xr.DataArray
        Radar reflectivity in dBZ with vcp_time dimension.
    a : float, optional
        Z-R relationship parameter (default: 200.0, Marshall-Palmer 1948).
    b : float, optional  
        Z-R relationship parameter (default: 1.6, Marshall-Palmer 1948).
    t : float, optional
        Integration time in minutes. If None, computed from vcp_time dimension.
    
    Returns:
    --------
    xr.DataArray
        Estimated rainfall depth (mm).
    """
    # Check for vcp_time dimension and compute integration time if not provided
    if t is None:
        if 'vcp_time' not in z.dims:
            raise ValueError("DataArray must have 'vcp_time' dimension or provide integration time 't'")

        # Compute time differences in minutes
        time_diffs = z.vcp_time.diff('vcp_time')
        integration_time = time_diffs.dt.total_seconds() / 60.0  # Convert to minutes
        
        # Use the median time difference as representative integration time
        t = float(integration_time.median().values)
        actual_total_minutes = float(integration_time.sum().values)
        actual_total_seconds = actual_total_minutes * 60

        # Convert to days, hours, minutes
        total_days = int(actual_total_seconds // 86400)
        remaining_seconds = actual_total_seconds % 86400
        total_hours = int(remaining_seconds // 3600)
        remaining_seconds = remaining_seconds % 3600
        total_minutes = int(remaining_seconds // 60)
        
        print(f"Actual QPE integration period: {total_days} days, {total_hours} hours, {total_minutes} minutes")
        print(f"Time span: {str(z.vcp_time.min().values)[:19]} to {str(z.vcp_time.max().values)[:19]} UTC")
    
    # Convert reflectivity from dBZ to linear units
    z_lin = 10 ** (z / 10) 
    
    # Compute rainfall depth using Z-R relationship and time integration
    depth = ((1 / a) ** (1 / b) * z_lin ** (1 / b)) * (t / 60)
    
    # Create new DataArray with proper name and attributes
    result = depth.copy()
    result.name = "rain_depth"
    result.attrs = {
        "units": "mm",
        "long_name": "rainfall depth",
        "standard_name": "rainfall_depth",
        "description": f"Estimated rainfall depth using Z-R relationship (a={a}, b={b})"
    }
    
    return result


def compute_qvp(ds: xr.Dataset, var="DBZH") -> xr.DataArray:
    """
    Computes a Quasi-Vertical Profile (QVP) from a radar time-series dataset.

    This function averages the specified variable over the azimuthal dimension
    to produce a QVP. If the variable is in dBZ (a logarithmic scale), it converts
    the values to linear units before averaging and then converts the result
    back to dBZ.
    """
    units: str = ds[var].attrs["units"]
    if units.startswith("dB"):
        qvp = 10 ** (ds[var] / 10)
        qvp = qvp.mean("azimuth", skipna=True)
        qvp = 10 * np.log10(qvp)
    else:
        qvp = ds[var]
        qvp = qvp.mean("azimuth", skipna=True)

    # computing heigth dimension
    qvp = qvp.assign_coords(
        {
            "range": (
                qvp.range.values
                * np.sin(ds.sweep_fixed_angle.mean(skipna=True).values * np.pi / 180.0)
            )
            / 1000
        }
    )

    qvp = qvp.rename(f"qvp_{var}")
    qvp = qvp.rename({"range": "height"})
    return qvp


def ryzhkov_figure(qvp_ref, qvp_zdr, qvp_rhohv, qvp_phidp):
    fig, axs = plt.subplots(2, 2, figsize=(8, 4), sharey=True, sharex=True)
    
    ## Reflectivity plot
    cf = qvp_ref.plot.contourf(
        x="vcp_time",
        y="height",
        cmap="ChaseSpectral",
        levels=np.arange(-10, 55, 1),
        ax=axs[0][0],
        add_colorbar=False,
    )
    contour_lines = qvp_ref.plot.contour(
        x="vcp_time",
        y="height",
        colors="k",  # Black contour lines
        levels=np.arange(0, 60, 15),  # Contour lines every 10 units
        ax=axs[0][0],
    )
    axs[0][0].clabel(contour_lines, fmt="%d", inline=True, fontsize=8)
    
    axs[0][0].set_title(r"$Z$")
    axs[0][0].set_xlabel("")
    axs[0][0].set_ylabel(r"$Height \ [km]$")
    axs[0][0].set_ylim(0, 12)
    
    cbar = plt.colorbar(
        cf,
        ax=axs[0][0],
        label=r"$Reflectivity \ [dBZ]$",
    )
    ## ZDR plot
    cf1 = qvp_zdr.plot.contourf(
        x="vcp_time",
        y="height",
        cmap="ChaseSpectral",
        ax=axs[0][1],
        levels=np.linspace(-2, 4, 21),
        add_colorbar=False,
    )
    
    contour_lines = qvp_ref.plot.contour(
        x="vcp_time",
        y="height",
        colors="k",  # Black contour lines
        levels=np.arange(0, 60, 15),  # Contour lines every 10 units
        ax=axs[0][1],
    )
    axs[0][1].clabel(contour_lines, fmt="%d", inline=True, fontsize=8)
    
    axs[0][1].set_title(r"$Z_{DR}$")
    axs[0][1].set_xlabel("")
    axs[0][1].set_ylabel(r"")
    
    cbar = plt.colorbar(
        cf1,
        ax=axs[0][1],
        label=r"$Diff. \ Reflectivity \ [dB]$",
    )
    
    ### RHOHV plot
    cf2 = qvp_rhohv.plot.contourf(
        x="vcp_time",
        y="height",
        cmap="Carbone11",
        ax=axs[1][0],
        levels=np.arange(0.7, 1.01, 0.01),
        add_colorbar=False,
    )
    
    contour_lines = qvp_ref.plot.contour(
        x="vcp_time",
        y="height",
        colors="k",  # Black contour lines
        levels=np.arange(0, 60, 15),  # Contour lines every 10 units
        ax=axs[1][0],
    )
    axs[1][0].clabel(contour_lines, fmt="%d", inline=True, fontsize=8)
    
    axs[1][0].set_title(r"$\rho _{HV}$")
    axs[1][0].set_ylabel(r"$Height \ [km]$")
    axs[1][0].set_xlabel(r"$Time \ [UTC]$")
    axs[1][0].tick_params(axis='x', labelsize=8) 

    cbar = plt.colorbar(
        cf2,
        ax=axs[1][0],
        label=r"$Cross-Correlation \ Coef.$",
    )
    
    ### PHIDP
    cf3 = qvp_phidp.plot.contourf(
        x="vcp_time",
        y="height",
        cmap="PD17",
        ax=axs[1][1],
        levels=np.arange(0, 360, 10),
        add_colorbar=False,
    )
    
    contour_lines = qvp_ref.plot.contour(
        x="vcp_time",
        y="height",
        colors="k",  # Black contour lines
        levels=np.arange(0, 60, 15),  # Contour lines every 10 units
        ax=axs[1][1],
    )
    axs[1][1].clabel(contour_lines, fmt="%d", inline=True, fontsize=8)
    
    axs[1][1].set_title(r"$\theta _{DP}$")
    axs[1][1].set_xlabel(r"$Time \ [UTC]$")
    axs[1][1].set_ylabel(r"")
    axs[1][1].tick_params(axis='x', labelsize=8) 
    cbar = plt.colorbar(
        cf3,
        ax=axs[1][1],
        label=r"$Differential \ Phase \ [deg]$",
    )
    
    return fig.tight_layout()


def list_nexrad_files(
    radar: str = "KVNX",
    start_time: str="2011-05-20 00:00",
    end_time: str="2011-05-20 23:59",
) -> list:
    """
    List NEXRAD Level II files from AWS S3 bucket for a given radar and time range.

    Parameters:
    -----------
    start_time : str
        Start time in format "YYYY-MM-DD HH:MM"
    end_time : str
        End time in format "YYYY-MM-DD HH:MM"
    radar : str
        Radar site code (e.g., "KVNX")

    Returns:
    --------
    List[str]
        List of S3 paths to NEXRAD Level II files within the specified time range.
    """

    # Parse input times
    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
    
    fs = fsspec.filesystem("s3", anon=True)
    base_path = "s3://noaa-nexrad-level2/"
    file_list = []

    current_dt = start_dt
    while current_dt <= end_dt:
        date_str = current_dt.strftime("%Y/%m/%d")
        prefix = f"{base_path}{date_str}/{radar}/{radar}"
        try:
            # Use glob to list files under this date/hour
            paths = fs.glob(f"{prefix}*")
            for path in paths:
                # Extract timestamp from filename
                filename = path.split("/")[-1]
                try:
                    file_time = datetime.strptime(filename[len(radar):len(radar)+15], "%Y%m%d_%H%M%S")
                    if start_dt <= file_time <= end_dt:
                        file_list.append(f"s3://{path}")
                except Exception:
                    continue
        except FileNotFoundError:
            pass

        current_dt += timedelta(days=1)

    return sorted(file_list)


def nexrad_donwload(s3filepath, compressed=True):
    storage_options = {"anon": True}
    if compressed:
        compression= "gzip"
    else:
        compression = None
    stream = fsspec.open(s3filepath, mode="rb", compression=compression, **storage_options).open()
    return xd.io.open_nexradlevel2_datatree(stream.read())
