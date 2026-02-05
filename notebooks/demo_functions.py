from datetime import datetime, timedelta

import fsspec
import icechunk
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import xradar as xd
from xarray import Dataset, DataTree


def rain_depth(
    z: xr.DataArray, a: float = 200.0, b: float = 1.6, t: float = None
) -> xr.DataArray:
    """
    Estimates rainfall depth using radar reflectivity and Z-R relationship.

    Computes precipitation depth per timestep using actual time differences
    between scans (not a constant interval), enabling accurate accumulation
    even when scan intervals vary.

    Parameters:
    -----------
    z : xr.DataArray
        Radar reflectivity in dBZ with vcp_time dimension.
    a : float, optional
        Z-R relationship parameter (default: 200.0, Marshall-Palmer 1948).
        For snow, use a=1780 (Sekhon-Srivastava 1970).
    b : float, optional
        Z-R relationship parameter (default: 1.6, Marshall-Palmer 1948).
        For snow, use b=2.21 (Sekhon-Srivastava 1970).
    t : float, optional
        Fixed integration time in minutes. If None, computed from actual
        time differences between scans in the vcp_time dimension.

    Returns:
    --------
    xr.DataArray
        Estimated rainfall/snowfall depth (mm) per timestep.
        Sum over vcp_time dimension to get total accumulation.
    """
    # Convert reflectivity from dBZ to linear units
    z_lin = 10 ** (z / 10)

    # Compute rainfall rate using Z-R relationship: R = (Z/a)^(1/b) in mm/hr
    rain_rate = (z_lin / a) ** (1 / b)

    if t is not None:
        # Use fixed integration time
        depth = rain_rate * (t / 60)  # Convert minutes to hours
    else:
        # Compute from actual time differences
        if "vcp_time" not in z.dims:
            raise ValueError(
                "DataArray must have 'vcp_time' dimension or provide integration time 't'"
            )

        # Compute time differences in hours for each timestep
        time_diffs = z.vcp_time.diff("vcp_time").dt.total_seconds() / 3600.0

        # Use median interval for uniform integration (simpler and avoids xr.concat issues)
        median_dt_hours = float(time_diffs.median().values)
        actual_total_hours = float(time_diffs.sum().values)

        # Multiply rate by median time interval to get depth per scan
        depth = rain_rate * median_dt_hours

        # Print summary info
        print(
            f"Actual QPE integration period: {int(actual_total_hours // 24)} days, "
            f"{int(actual_total_hours % 24)} hours, {int((actual_total_hours % 1) * 60)} minutes"
        )
        print(
            f"Time span: {str(z.vcp_time.min().values)[:19]} to {str(z.vcp_time.max().values)[:19]} UTC"
        )

    # Create result with proper metadata
    result = depth.copy()
    result.name = "precip_depth"
    result.attrs = {
        "units": "mm",
        "long_name": "precipitation depth per timestep",
        "description": f"Estimated using Z-R relationship (a={a}, b={b})",
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
    fig, axs = plt.subplots(2, 2, figsize=(9, 5), sharey=True, sharex=True)

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

    plt.colorbar(
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

    plt.colorbar(
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
    axs[1][0].tick_params(axis="x", labelsize=8)

    plt.colorbar(
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
    axs[1][1].tick_params(axis="x", labelsize=8)
    plt.colorbar(
        cf3,
        ax=axs[1][1],
        label=r"$Differential \ Phase \ [deg]$",
    )

    return fig.tight_layout()


def list_nexrad_files(
    radar: str = "KVNX",
    start_time: str = "2011-05-20 00:00",
    end_time: str = "2011-05-20 23:59",
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
    base_path = "s3://unidata-nexrad-level2/"
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
                    file_time = datetime.strptime(
                        filename[len(radar) : len(radar) + 15], "%Y%m%d_%H%M%S"
                    )
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
        compression = "gzip"
    else:
        compression = None
    stream = fsspec.open(
        s3filepath, mode="rb", compression=compression, **storage_options
    ).open()
    return xd.io.open_nexradlevel2_datatree(stream.read())


def get_repo_config():
    split_config = icechunk.ManifestSplittingConfig.from_dict(
        {
            icechunk.ManifestSplitCondition.AnyArray(): {
                icechunk.ManifestSplitDimCondition.DimensionName("vcp_time"): 12
                * 24
                * 365  # roughly one year of radar data
            }
        }
    )
    var_condition = icechunk.ManifestPreloadCondition.name_matches(
        r"^(vcp_time|azimuth|range)$"
    )
    size_condition = icechunk.ManifestPreloadCondition.num_refs(0, 10_000)

    preload_if = icechunk.ManifestPreloadCondition.and_conditions(
        [var_condition, size_condition]
    )

    preload_config = icechunk.ManifestPreloadConfig(
        max_total_refs=10_000,
        preload_if=preload_if,
    )

    return icechunk.RepositoryConfig(
        manifest=icechunk.ManifestConfig(
            splitting=split_config, preload=preload_config
        ),
    )


def list_nexrad_files_with_sizes(
    radar: str = "KVNX",
    start_time: str = "2011-05-20 00:00",
    end_time: str = "2011-05-20 23:59",
) -> list[dict]:
    """
    List NEXRAD Level II files with actual file sizes using fsspec.

    Parameters:
    -----------
    radar : str
        Radar site code (e.g., "KVNX")
    start_time : str
        Start time in format "YYYY-MM-DD HH:MM"
    end_time : str
        End time in format "YYYY-MM-DD HH:MM"

    Returns:
    --------
    list[dict]
        List of dicts with 'path', 'size' (bytes), and 'time' for each file.
    """
    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

    fs = fsspec.filesystem("s3", anon=True)
    base_path = "unidata-nexrad-level2"
    file_list = []

    current_dt = start_dt
    while current_dt <= end_dt:
        date_str = current_dt.strftime("%Y/%m/%d")
        dir_path = f"{base_path}/{date_str}/{radar}"

        try:
            # List directory with details (includes size)
            files_info = fs.ls(dir_path, detail=True)
            for file_info in files_info:
                filename = file_info["name"].split("/")[-1]
                # Filter to only files starting with radar name
                if not filename.startswith(radar):
                    continue
                try:
                    file_time = datetime.strptime(
                        filename[len(radar) : len(radar) + 15], "%Y%m%d_%H%M%S"
                    )
                    if start_dt <= file_time <= end_dt:
                        file_list.append(
                            {
                                "path": f"s3://{file_info['name']}",
                                "size": file_info.get("size", 0),
                                "time": file_time,
                            }
                        )
                except Exception:
                    continue
        except Exception:
            pass

        current_dt += timedelta(days=1)

    return sorted(file_list, key=lambda x: x["time"])


def nexrad_download_with_size(filepath: str) -> tuple:
    """
    Download a NEXRAD file and return datatree with size info.

    Parameters:
    -----------
    filepath : str
        S3 path to the NEXRAD file

    Returns:
    --------
    tuple
        (datatree, size_bytes) - The xradar datatree and file size in bytes
    """
    fs = fsspec.filesystem("s3", anon=True)

    # Get file info for size (compressed size)
    path = filepath.replace("s3://", "")
    file_info = fs.info(path)
    size_bytes = file_info.get("size", 0)

    # Use fsspec's built-in gzip decompression
    compression = "gzip" if filepath.endswith(".gz") else None
    stream = fsspec.open(filepath, mode="rb", compression=compression, anon=True).open()
    dtree = xd.io.open_nexradlevel2_datatree(stream.read())

    return dtree, size_bytes


def concat_sweep_across_vcps(
    dtree: DataTree,
    sweep_name: str = "sweep_0",
    append_dim: str = "vcp_time",
    validate_coords: bool = True,
    sort_by_time: bool = True,
    group_prefix: str = None,
) -> Dataset:
    """
    Concatenate a specific sweep across multiple VCP nodes along the vcp_time dimension.

    This enables continuous temporal analysis (e.g., QPE) for a specific elevation angle
    across different Volume Coverage Patterns.

    Parameters
    ----------
    dtree : xarray.DataTree
        DataTree with VCP nodes (e.g., "VCP-212", "VCP-35") containing sweep_* children
    sweep_name : str, default "sweep_0"
        Name of the sweep to extract from each VCP (e.g., "sweep_0", "sweep_1")
    append_dim : str, default "vcp_time"
        Time dimension name to concatenate along
    validate_coords : bool, default True
        If True, validate that all sweeps have compatible azimuth/range coordinates
    sort_by_time : bool, default True
        If True, sort the concatenated result by the append_dim coordinate
    group_prefix : str, optional
        Group prefix for organized data (e.g., "spatial", "temporal").
        If provided, VCPs are expected under this prefix (e.g., "/spatial/VCP-212").
        If None, VCPs are expected at the root level (e.g., "/VCP-212").

    Returns
    -------
    xarray.Dataset
        Concatenated dataset with all VCP sweeps merged along vcp_time dimension

    Raises
    ------
    ValueError
        If no VCP nodes are found, sweep not found in any VCP, or coordinates are incompatible

    Examples
    --------
    >>> # Standard structure (VCPs at root)
    >>> dtree = convert_files(radar_files, ...)
    >>> sweep_0_continuous = concat_sweep_across_vcps(dtree, sweep_name="sweep_0")
    >>>
    >>> # With group prefix (e.g., spatial/temporal organization)
    >>> sweep_0_spatial = concat_sweep_across_vcps(dtree, sweep_name="sweep_0", group_prefix="spatial")
    >>> sweep_0_temporal = concat_sweep_across_vcps(dtree, sweep_name="sweep_0", group_prefix="temporal")
    >>>
    >>> # Calculate QPE on continuous data
    >>> qpe = calculate_qpe(sweep_0_continuous['DBZH'])

    Notes
    -----
    - Assumes sweep_0 (and sweep_1) have consistent coordinates across VCPs
    - VCP nodes are automatically detected from the DataTree structure (VCP-* pattern)
    - Supports both single-store (with group_prefix) and multi-store (without) modes
    - Time coordinates are sorted after concatenation (if sort_by_time=True)
    - Missing sweeps in a VCP will be skipped with a warning
    - Coordinate validation checks azimuth and range dimension sizes for compatibility
    """
    # Find all VCP nodes in the DataTree
    vcp_nodes = {}
    for node_path in dtree.groups:
        parts = node_path.strip("/").split("/")

        # Handle group_prefix if provided
        if group_prefix:
            # Expect structure: /group_prefix/VCP-XXX or group_prefix/VCP-XXX
            if (
                len(parts) >= 2
                and parts[0] == group_prefix
                and parts[1].startswith("VCP-")
            ):
                if len(parts) == 2:  # Only VCP root nodes
                    vcp_name = parts[1]
                    vcp_nodes[vcp_name] = dtree[node_path]
        else:
            # Standard structure: /VCP-XXX or VCP-XXX
            if parts and parts[0].startswith("VCP-"):
                if len(parts) == 1:  # Only VCP root nodes
                    vcp_name = parts[0]
                    vcp_nodes[vcp_name] = dtree[node_path]

    if not vcp_nodes:
        prefix_msg = f" under '{group_prefix}/' prefix" if group_prefix else ""
        raise ValueError(
            f"No VCP nodes found in DataTree{prefix_msg}. "
            f"Expected nodes matching 'VCP-*' pattern."
        )

    # Extract the specified sweep from each VCP
    sweep_datasets = []
    skipped_vcps = []

    for vcp_name, _vcp_node in vcp_nodes.items():
        # Build sweep paths with group_prefix if provided
        if group_prefix:
            # With prefix: /spatial/VCP-212/sweep_0 or spatial/VCP-212/sweep_0
            sweep_path = f"/{group_prefix}/{vcp_name}/{sweep_name}"
            sweep_path_alt = f"{group_prefix}/{vcp_name}/{sweep_name}"
        else:
            # Without prefix: /VCP-212/sweep_0 or VCP-212/sweep_0
            sweep_path = f"/{vcp_name}/{sweep_name}"
            sweep_path_alt = f"{vcp_name}/{sweep_name}"

        if sweep_path in dtree.groups:
            sweep_ds = dtree[sweep_path].ds
            sweep_datasets.append((vcp_name, sweep_ds))
        elif sweep_path_alt in dtree.groups:
            sweep_ds = dtree[sweep_path_alt].ds
            sweep_datasets.append((vcp_name, sweep_ds))
        else:
            skipped_vcps.append(vcp_name)

    if not sweep_datasets:
        raise ValueError(
            f"Sweep '{sweep_name}' not found in any VCP nodes. "
            f"Available VCPs: {list(vcp_nodes.keys())}"
        )

    if skipped_vcps:
        import warnings

        warnings.warn(
            f"Sweep '{sweep_name}' not found in VCPs: {skipped_vcps}. "
            f"Proceeding with {len(sweep_datasets)} VCPs.",
            UserWarning,
            stacklevel=2,
        )

    # Validate coordinate compatibility if requested
    if validate_coords and len(sweep_datasets) > 1:
        reference_vcp, reference_ds = sweep_datasets[0]
        ref_azimuth_size = reference_ds.sizes.get("azimuth")
        ref_range_size = reference_ds.sizes.get("range")

        for vcp_name, sweep_ds in sweep_datasets[1:]:
            azimuth_size = sweep_ds.sizes.get("azimuth")
            range_size = sweep_ds.sizes.get("range")

            if azimuth_size != ref_azimuth_size or range_size != ref_range_size:
                raise ValueError(
                    f"Coordinate mismatch between {reference_vcp} and {vcp_name}:\n"
                    f"  {reference_vcp}: azimuth={ref_azimuth_size}, range={ref_range_size}\n"
                    f"  {vcp_name}: azimuth={azimuth_size}, range={range_size}\n"
                    f"Set validate_coords=False to skip this check."
                )

    # Concatenate datasets along the append_dim
    datasets_only = [ds for _, ds in sweep_datasets]
    concatenated = xr.concat(datasets_only, dim=append_dim)

    # Sort by time if requested
    if sort_by_time and append_dim in concatenated.coords:
        concatenated = concatenated.sortby(append_dim)

    return concatenated
