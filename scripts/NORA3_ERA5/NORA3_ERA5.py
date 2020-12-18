"""NORA3 and ERA5 tools. 

Install requirements with pip3 install -r requirements.txt
"""

#%%
import netCDF4 as nc4
import numpy as np
import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

def get_timeseries(param, lon, lat, start_time, end_time, use_atm=True):
    """Time series extraction from NORA3 and ERA5.

    NOTE: Use ERA5 parameter names. See atm_params_nora3 for NORA3 equivalents

    Returns tuple with string "NORA3" or "ERA5" depending on which data set was
    used, and time series xarray for parameter param at location (lat, lon) in 
    interval [start_time, end_time] with a temporal resolution of one hour. If 
    NORA3 data is not available for the given location and the full time 
    interval, ERA5 data will be used. The nearest grid point will be used.

    Data directories: 
    /lustre/storeB/project/fou/om/ERA/ERA5 [1979-1, 2019-12]
    /lustre/storeB/project/fou/om/WINDSURFER/HM40h12/netcdf [1997-08, 2019-12]
    """
    available_atm_params = ["msl", "u10", "v10"]
    available_wave_params = ["msl", "mwd", "mp2", "pp1d", "swh"]

    atm_params_nora3 = {
        "msl": "air_pressure_at_sea_level",
        "u10": "x_wind_10m",
        "v10": "y_wind_10m"
    }

    # sanity check arguments
    if param not in available_atm_params and param not in available_wave_params:
        raise RuntimeError("Undefined parameter: " + param)
    if datetime(2019, 12, 31) < start_time or start_time < datetime(1979, 1, 1):
        raise RuntimeError("Start time outside data set time interval")
    if datetime(2019, 12, 31) < end_time or end_time < datetime(1979, 1, 1):
        raise RuntimeError("End time outside data set time interval")

    # inside time interval and domain for NORA3?
    if start_time >= datetime(1997, 8, 1, 4, 0, 0) and (44.0 <= lat <= 83.0) and (-30.0 <= lon <= 85.0):
        return ("NORA3", get_nora3_timeseries(atm_params_nora3[param], lat, lon, start_time, end_time))
    else:
        return ("ERA5", get_era5_timeseries(param, lat, lon, start_time, end_time, use_atm))

def get_era5_timeseries(param, lon, lat, start_time, end_time, use_atm=True):
    """Time series extraction from ERA5.

    Returns time series xarray for parameter param at location (lat, lon) in interval
    [start_time, end_time] with a temporal resolution of one hour. The nearest 
    grid point will be used.

    TODO: Selection of the nearest wet (not missing_value) point for wave params using
    xarray. This is not straightforward to implement at this point
    (see also https://github.com/pydata/xarray/issues/644)

    Data directories: 
    /lustre/storeB/project/fou/om/ERA/ERA5 [1979-1, 2019-12]
    """
    data_dir = "/lustre/storeB/project/fou/om/ERA/ERA5"
    available_atm_params = ["msl", "u10", "v10"]
    available_wave_params = ["msl", "mwd", "mp2", "pp1d", "swh"]
    
    # sanity check arguments
    if param not in available_atm_params and param not in available_wave_params:
        raise RuntimeError("Undefined parameter: " + param)
    if -90.0 > lat > 90.0:
        raise RuntimeError("Latitude (lat) must be in the interval [-90.0, 90.0]")
    if 0.0 > lon >= 360.0:
        raise RuntimeError("Longitude (lon) must be in the interval [0.0, 360.0)")
    
    #print("From " + start_time.strftime("%Y%m-%H%M"))
    #print("To " + end_time.strftime("%Y%m-%H%M"))

    # find and open correct netCDF file(s)
    filenames = []
    month_count = (end_time.year - start_time.year) * 12 + (end_time.month - start_time.month) + 1
    
    #print("Months:" + str(month_count))

    if param in available_atm_params and use_atm:
        for month in (start_time + relativedelta(months=+n) for n in range(month_count)):
            filenames.append(os.path.join(data_dir, "atm/era5_atm_CDS_{}.nc".format(month.strftime("%Y%m"))))
    elif param in available_wave_params:
        for month in (start_time + relativedelta(months=+n) for n in range(month_count)):
            filenames.append(os.path.join(data_dir, "wave/era5_wave_CDS_{}.nc".format(month.strftime("%Y%m"))))
    else:
        raise RuntimeError(param + " is not found in ERA5 wave data set (try use_atm=True)")
    
    era5 = xr.open_mfdataset(filenames, parallel=True, autoclose=True)

    # extract data set
    era5_da = era5[param].sel(longitude=lon, latitude=lat, method="nearest")
    era5_da = era5_da.sel(time=slice(start_time, end_time))

    # return time series as xarray
    return era5_da

def get_nora3_timeseries(param, lon, lat, start_time, end_time):
    """Time series extraction from NORA3.

    Returns time series xarray for parameter param at location (lat, lon) in interval
    [start_time, end_time] with a temporal resolution of one hour. The nearest 
    grid point will be used.

    Data directories: 
    /lustre/storeB/project/fou/om/WINDSURFER/HM40h12/netcdf [1997-08, 2019-12]
    """
    data_dir = "/lustre/storeB/project/fou/om/WINDSURFER/HM40h12/netcdf"
    available_atm_params = ["air_pressure_at_sea_level", "x_wind_10m", "y_wind_10m"]

    # sanity check arguments
    if param not in available_atm_params:
        raise RuntimeError("Undefined parameter: " + param)
    if 44.0 > lat > 83.0:
        raise RuntimeError("Latitude (lat) must be in the interval [44.0, 83.0]")
    if -30.0 > lon > 85.0:
        raise RuntimeError("Longitude (lon) must be in the interval [-30.0, 85.0]")
    
    #print("From " + start_time.strftime("%Y%m%d-%H"))
    #print("To " + end_time.strftime("%Y%m%d-%H"))

    # find and open correct netCDF file(s)
    filenames = []
    hour = timedelta(hours=1)
    current_time = start_time

    if param in available_atm_params:
        while current_time <= end_time:
            current_time_with_offset = current_time - timedelta(hours=4)
            
            # find correct period folder
            if current_time_with_offset.hour < 6:
                period = 0
            elif current_time_with_offset.hour < 12:
                period = 6
            elif current_time_with_offset.hour < 18:
                period = 12
            else:
                period = 18
            
            # find correct index file
            index_file = current_time.hour - period
            if index_file < 0:
                index_file += 24

            filenames.append(
                os.path.join(data_dir, "{year}/{month}/{day}/{period:02d}/fc{year}{month}{day}{period:02d}_00{index_file}_fp.nc" \
                .format(year=current_time_with_offset.strftime("%Y"), 
                        month=current_time_with_offset.strftime("%m"), 
                        day=current_time_with_offset.strftime("%d"), 
                        period=period, index_file=index_file)))
            current_time += hour
    else:
        raise RuntimeError(param + " is not found in NORA3 data set")
    
    nora3 = xr.open_mfdataset(filenames, autoclose=True)

    # find coordinates in data set projection by transformation:
    #data_crs = ccrs.LambertConformal(central_longitude=-42.0, central_latitude=66.3,
    #            standard_parallels=[66.3, 66.3], 
    #            globe=ccrs.Globe(datum="WGS84",
    #            semimajor_axis=6371000.0))
    #x, y = data_crs.transform_point(lon, lat, src_crs=ccrs.PlateCarree())

    #nora3_da_lon = nora3["longitude"].sel(x=x, y=y, method="nearest")
    #nora3_da_lat = nora3["latitude"].sel(x=x, y=y, method="nearest")
    #print("Projected lon, lat: " + str(nora3_da_lon.values) + ", " + str(nora3_da_lat.values))
    
    # find coordinates in data set projection by lookup in lon-lat variables
    abslat = np.abs(nora3.latitude-lat)
    abslon = np.abs(nora3.longitude-lon)
    cor = np.maximum(abslon, abslat)
    ([y_idx], [x_idx]) = np.where(cor == np.min(cor))

    #print("Projected lon, lat: " 
    #        + str(nora3["longitude"].isel(x=x_idx, y=y_idx).values) + ", " 
    #        + str(nora3["latitude"].isel(x=x_idx, y=y_idx).values))

    # extract data set
    #nora3_da = nora3[param].sel(x=x, y=y, method="nearest")
    nora3_da = nora3[param].isel(x=x_idx, y=y_idx)
    nora3_da = nora3_da.sel(time=slice(start_time, end_time))

    # return time series as xarray
    return nora3_da

if __name__ == "__main__":
    # TODO: fix memory prob with to_netcdf(),
    #       find nearest "wet point" and describe difference in latlon for these stations, 
    #       (see https://gitlab.met.no/jeanr/interact_with_roms/-/tree/master/lat_lon_to_ROMS_timeseries)
    #       extract functions (choose time stride, parameter, input and output filenames),
    #       produce full ERA5 timeseries for all params on PPI

    # write msl timeseries for the complete ERA5 period for
    # every observation in obs data file (see line below)
    aggr_water_level_data = xr.open_mfdataset(
        "/lustre/storeB/project/IT/geout/machine-ocean/prepared_datasets/storm_surge/aggregated_water_level_data/aggregated_water_level_observations_with_pytide_prediction_dataset.nc4")

    station_ids = aggr_water_level_data["stationid"]
    station_lons = aggr_water_level_data["longitude"]
    station_lats = aggr_water_level_data["latitude"]

    out_da = xr.Dataset()
    out_da["stationid"] = station_ids
    out_da["longitude_station"] = station_lons
    out_da["latitude_station"] = station_lats

    dataarrays = []
    for (station_id, station_lon, station_lat) in zip(station_ids, station_lons, station_lats):
        print("Writing timeseries for station " + str(station_id.values) + " at " 
                + str(station_lon.values) + ", " + str(station_lat.values))

        da = get_era5_timeseries("msl", station_lon, station_lat, 
                datetime(1979, 1, 1, 18), datetime(1979, 1, 1, 19))#datetime(2019, 12, 31))
        
        dataarrays.append(da)
    
    combined = xr.concat(dataarrays, dim="station")

    out_da["msl"] = combined

    # ensure CF compliance
    out_da.attrs["Conventions"] = "CF-1.8"
    out_da["longitude"].attrs["units"] = "degrees_east"
    out_da["longitude"].attrs["long_name"] = "longitude"
    out_da["longitude"].attrs["description"] = "longitude of closest data point to station"

    out_da["longitude_station"].attrs["units"] = "degrees_east"
    out_da["longitude_station"].attrs["long_name"] = "longitude_station"

    out_da["latitude"].attrs["units"] = "degrees_north"
    out_da["latitude"].attrs["long_name"] = "latitude"
    out_da["latitude"].attrs["description"] = "latitude of closest data point to station"

    out_da["latitude_station"].attrs["units"] = "degrees_north"
    out_da["latitude_station"].attrs["long_name"] = "latitude_station"

    print(out_da)
    out_da.to_netcdf("aggregated_era5_data_incomplete_test.nc", 
                        format="NETCDF4", engine="netcdf4", unlimited_dims="time",
                        encoding={"msl": {"dtype": "float32", "zlib": False, "_FillValue": 1.0e37}})

    # %%
